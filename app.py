from flask import Flask, render_template, request, jsonify
import json
import heapq

app = Flask(__name__)

# Define the FCFS function
def fcfs(process_list):
     current_time = 0  # Current time of the CPU
     gantt_chart = []  # Stores the processes sequence
     results = []  # Stores completion results for each process
     total_waiting_time = 0
     total_turnaround_time = 0
     total_response_time = 0
 
     # Sort processes by arrival time
     process_list.sort(key=lambda x: x[0])
 
     for process in process_list:
         arrival = process[0]
         burst = process[1]
         pid = process[2]
 
         # Idle time calculation
         if arrival > current_time:
             gantt_chart.append("Idle")
             current_time = arrival
 
         # Process execution and results calculation
         gantt_chart.append(pid)
         start_time = current_time
         completion_time = start_time + burst
         turnaround_time = completion_time - arrival
         waiting_time = turnaround_time - burst
         response_time = current_time - arrival
         
 
         # Store the results for each process
         results.append({
             "Process Name": pid,
             "Arrival Time": arrival,
             "Burst Time": burst,
             "Start Time": start_time,
             "Completion Time": completion_time,
             "Turnaround Time": turnaround_time,
             "Waiting Time": waiting_time,
             "Response Time": response_time
         })
 
         # Update the total times
         total_waiting_time += waiting_time
         total_turnaround_time += turnaround_time
         total_response_time += response_time
 
         # Update current time with the end time of the process
         current_time = completion_time
 
     # Calculate the averages
     num_processes = len(process_list)
     avg_waiting_time = total_waiting_time / num_processes
     avg_turnaround_time = total_turnaround_time / num_processes
     avg_response_time = total_response_time / num_processes
 
     return gantt_chart, results, avg_waiting_time, avg_turnaround_time, avg_response_time


def sjf_non_preemptive(process_list):
    current_time = 0
    gantt_chart = []
    results = []
    total_waiting_time = 0
    total_turnaround_time = 0
    total_response_time = 0

    # Add unique index to maintain input order
    for i, process in enumerate(process_list):
        process.append(i)  # Append index

    original_burst_times = {process[2]: process[1] for process in process_list}
    process_list.sort(key=lambda x: x[0])
    num_processes = len(process_list)

    while len(results) < num_processes:
        available_processes = [p for p in process_list if p[0] <= current_time]
        if not available_processes:
            gantt_chart.append("Idle")
            current_time += 1
            continue

        # Sort available processes by Burst Time
        available_processes.sort(key=lambda x: x[1])
        process = available_processes[0]

        arrival, burst, pid, _ = process
        process_list.remove(process)

        if arrival > current_time:
            gantt_chart.append("Idle")
            current_time = arrival

        gantt_chart.append(pid)
        start_time = current_time
        completion_time = start_time + burst
        turnaround_time = completion_time - arrival
        waiting_time = turnaround_time - burst
        response_time = start_time - arrival

        results.append({
            "Process Name": pid,
            "Arrival Time": arrival,
            "Burst Time": original_burst_times[pid],
            "Start Time": start_time,
            "Completion Time": completion_time,
            "Turnaround Time": turnaround_time,
            "Waiting Time": waiting_time,
            "Response Time": response_time,
            "Index": process[3]  # Keep the index
        })

        total_waiting_time += waiting_time
        total_turnaround_time += turnaround_time
        total_response_time += response_time

        current_time = completion_time

    # Sort results by input order (index)
    results.sort(key=lambda x: x["Index"])
    for result in results:
        del result["Index"]  # Remove the index from final output

    avg_waiting_time = total_waiting_time / num_processes
    avg_turnaround_time = total_turnaround_time / num_processes
    avg_response_time = total_response_time / num_processes

    return gantt_chart, results, avg_waiting_time, avg_turnaround_time, avg_response_time

import heapq

def sjf_preemptive(process_list):
    current_time = 0
    gantt_chart = []
    results = []
    total_waiting_time = 0
    total_turnaround_time = 0
    total_response_time = 0

    # Add unique index to maintain input order
    for i, process in enumerate(process_list):
        process.append(i)  # Append index

    original_burst_times = {process[2]: process[1] for process in process_list}
    process_list.sort(key=lambda x: x[0])
    num_processes = len(process_list)
    process_queue = []
    remaining_burst_times = {process[2]: process[1] for process in process_list}
    start_times = {}
    completed_processes = 0

    while completed_processes < num_processes:
        while process_list and process_list[0][0] <= current_time:
            arrival, burst, pid, idx = process_list.pop(0)
            heapq.heappush(process_queue, (remaining_burst_times[pid], arrival, pid, idx))

        if not process_queue:
            gantt_chart.append("Idle")
            current_time += 1
            continue

        burst, arrival, pid, idx = heapq.heappop(process_queue)

        if pid not in start_times:
            start_times[pid] = current_time

        if not gantt_chart or gantt_chart[-1] != pid:
            gantt_chart.append(pid)

        current_time += 1
        remaining_burst_times[pid] -= 1

        if remaining_burst_times[pid] == 0:
            completion_time = current_time
            turnaround_time = completion_time - arrival
            waiting_time = turnaround_time - original_burst_times[pid]
            response_time = start_times[pid] - arrival

            results.append({
                "Process Name": pid,
                "Arrival Time": arrival,
                "Burst Time": original_burst_times[pid],
                "Start Time": start_times[pid],
                "Completion Time": completion_time,
                "Turnaround Time": turnaround_time,
                "Waiting Time": waiting_time,
                "Response Time": response_time,
                "Index": idx  # Keep the index
            })

            total_waiting_time += waiting_time
            total_turnaround_time += turnaround_time
            total_response_time += response_time
            completed_processes += 1
        else:
            heapq.heappush(process_queue, (remaining_burst_times[pid], arrival, pid, idx))

    # Sort results by input order (index)
    results.sort(key=lambda x: x["Index"])
    for result in results:
        del result["Index"]  # Remove the index from final output

    avg_waiting_time = total_waiting_time / num_processes
    avg_turnaround_time = total_turnaround_time / num_processes
    avg_response_time = total_response_time / num_processes

    return gantt_chart, results, avg_waiting_time, avg_turnaround_time, avg_response_time



def round_robin(process_list, time_quantum):
    current_time = 0
    gantt_chart = []
    results = []
    total_waiting_time = 0
    total_turnaround_time = 0
    total_response_time = 0

    
    process_list_original = list(process_list)

    remaining_burst_times = {process[2]: process[1] for process in process_list}
    response_times = {}
    start_times = {}
    queue = []
    process_list.sort(key=lambda x: x[0])

    num_processes = len(process_list)
    completed_processes = 0

    while process_list and process_list[0][0] <= current_time:
        arrival, burst, pid = process_list.pop(0)
        queue.append((arrival, burst, pid))

    while completed_processes < num_processes:
        if not queue:
            gantt_chart.append("Idle")
            current_time += 1
            while process_list and process_list[0][0] <= current_time:
                arrival, burst, pid = process_list.pop(0)
                queue.append((arrival, burst, pid))
            continue

        arrival, burst, pid = queue.pop(0)

        if pid not in response_times:
            response_times[pid] = max(0, current_time - arrival)

        if pid not in start_times:
            start_times[pid] = current_time

        if not gantt_chart or gantt_chart[-1] != pid:
            gantt_chart.append(pid)

        executed_time = min(time_quantum, remaining_burst_times[pid])
        current_time += executed_time
        remaining_burst_times[pid] -= executed_time

        while process_list and process_list[0][0] <= current_time:
            new_arrival, new_burst, new_pid = process_list.pop(0)
            queue.append((new_arrival, new_burst, new_pid))

        if remaining_burst_times[pid] > 0:
            queue.append((arrival, burst, pid))
        else:
            completion_time = current_time
            turnaround_time = completion_time - arrival
            waiting_time = turnaround_time - burst

            results.append({
                "process_name": pid,
                "arrival_time": arrival,
                "burst_time": burst,
                "start_time": start_times[pid],
                "completion_time": completion_time,
                "turnaround_time": turnaround_time,
                "waiting_time": waiting_time,
                "response_time": response_times[pid],
            })

            total_waiting_time += waiting_time
            total_turnaround_time += turnaround_time
            total_response_time += response_times[pid]
            completed_processes += 1

    ordered_results = sorted(results, key=lambda r: [process[2] for process in process_list_original].index(r["process_name"]))

    avg_waiting_time = total_waiting_time / num_processes
    avg_turnaround_time = total_turnaround_time / num_processes
    avg_response_time = total_response_time / num_processes

    return gantt_chart, ordered_results, avg_waiting_time, avg_turnaround_time, avg_response_time

 # Route for the FCFS page (HTML)
@app.route("/")
def index():
     return render_template("index.html")

@app.route("/fcfs")
def fcfs_page():
     return render_template("fcfs.html") 

@app.route("/sjf")
def sjf():
     return render_template("sjf.html") 

@app.route("/rr")
def rr():
     return render_template("rr.html")

@app.route("/priority")
def priority():
     return render_template("priority.html")

@app.route("/process", methods=["POST"])
def process():
    # Get the JSON string from the hidden field
    data = request.form.get("processes")
    scheduling_type = request.form.get("scheduling_type")
    time_quantum = request.form.get("time_quantum")
    print("Received processes:", data)  # Added print
    print("Scheduling type:", scheduling_type)  # Added print
    try:
        processes = json.loads(data)
        print("Parsed processes:", processes) # added print
    except:
         return jsonify(error_message="Error parsing processes data.")

    # Error handling: Check for empty or invalid inputs
    error_message = None

    processes_for_sort = []
    for process in processes:
        process_name = process["process_name"]
        arrival_time = process["arrival_time"]
        burst_time = process["burst_time"]

        if not arrival_time and not burst_time:
            error_message = "Error: Arrival Time and Burst Time must be filled."
            break
        #Error handeling for invalid input
        try:
            arrival_time_int = int(arrival_time)
            burst_time_int = int(burst_time)
        except ValueError:
            error_message = "Error: Arrival Time and Burst Time must be valid integers."
            break

        processes_for_sort.append([arrival_time_int, burst_time_int, process_name])

    print("Processes for Sort:", processes_for_sort) # added print
    
    if error_message:
        return jsonify(error_message=error_message)
    
    #Error handling for quantum time
    if scheduling_type == "rr":
          if not time_quantum:
             return jsonify(error_message="Please enter quantum time.")
          try:
               time_quantum_int = int(time_quantum)
               if time_quantum_int <= 0:
                  return jsonify(error_message="Quantum time must be greater than 0.")
          except ValueError:
                return jsonify(error_message="Quantum time must be a valid number.")
    # Call the scheduling algorithm function with the user input
    if scheduling_type == "fcfs":
         gantt_chart, results, avg_waiting_time, avg_turnaround_time, avg_response_time = fcfs(processes_for_sort)
    elif scheduling_type == "preemptive":
        gantt_chart, results, avg_waiting_time, avg_turnaround_time, avg_response_time = sjf_preemptive(processes_for_sort)
    elif scheduling_type == "non-preemptive":
        gantt_chart, results, avg_waiting_time, avg_turnaround_time, avg_response_time = sjf_non_preemptive(processes_for_sort)
    elif scheduling_type == "rr":
        gantt_chart, results, avg_waiting_time, avg_turnaround_time, avg_response_time = round_robin(processes_for_sort, time_quantum_int)
    else:
         return jsonify(error_message = "Select a scheduling type!")

    return jsonify(gantt_chart=gantt_chart, results=results,
                           avg_waiting_time=avg_waiting_time, avg_turnaround_time=avg_turnaround_time, avg_response_time=avg_response_time)
 
if __name__ == "__main__":
     app.run(debug=True)