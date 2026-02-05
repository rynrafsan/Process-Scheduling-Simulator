#include <stdio.h>
#include <string.h>
#include <limits.h>

typedef struct {
    char name[10];
    int arrival_time;
    int burst_time;
    int remaining_time;
    int waiting_time;
    int turnaround_time;
    int completion_time;
    int is_completed; 
} Process;

// Helper: Sort by Arrival
void sort_by_arrival(Process p[], int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (p[j].arrival_time > p[j+1].arrival_time) {
                Process temp = p[j];
                p[j] = p[j+1];
                p[j+1] = temp;
            }
        }
    }
}

// 1. FCFS
void calculate_fcfs(Process p[], int n) {
    sort_by_arrival(p, n);
    int current_time = 0;
    for (int i = 0; i < n; i++) {
        if (current_time < p[i].arrival_time) current_time = p[i].arrival_time;
        p[i].completion_time = current_time + p[i].burst_time;
        p[i].turnaround_time = p[i].completion_time - p[i].arrival_time;
        p[i].waiting_time = p[i].turnaround_time - p[i].burst_time;
        current_time += p[i].burst_time;
    }
}

// 2. SJF (Non-Preemptive)
void calculate_sjf(Process p[], int n) {
    int current_time = 0;
    int completed = 0;
    for(int i=0; i<n; i++) p[i].is_completed = 0;

    // Handle idle time if no process starts at 0
    int min_arrival = INT_MAX;
    for(int i=0; i<n; i++) if(p[i].arrival_time < min_arrival) min_arrival = p[i].arrival_time;
    if (current_time < min_arrival) current_time = min_arrival;

    while (completed < n) {
        int idx = -1;
        int min_burst = INT_MAX;
        
        for (int i = 0; i < n; i++) {
            if (p[i].arrival_time <= current_time && p[i].is_completed == 0) {
                if (p[i].burst_time < min_burst) {
                    min_burst = p[i].burst_time;
                    idx = i;
                }
                else if (p[i].burst_time == min_burst) {
                    if (idx != -1 && p[i].arrival_time < p[idx].arrival_time) {
                        idx = i;
                    }
                }
            }
        }

        if (idx != -1) {
            current_time += p[idx].burst_time;
            p[idx].completion_time = current_time;
            p[idx].turnaround_time = p[idx].completion_time - p[idx].arrival_time;
            p[idx].waiting_time = p[idx].turnaround_time - p[idx].burst_time;
            p[idx].is_completed = 1;
            completed++;
        } else {
            current_time++;
        }
    }
}

// 3. SRTF (Preemptive)
void calculate_srtf(Process p[], int n) {
    int current_time = 0;
    int completed = 0;
    for(int i=0; i<n; i++) p[i].remaining_time = p[i].burst_time;

    // Handle idle start
    int min_arrival = INT_MAX;
    for(int i=0; i<n; i++) if(p[i].arrival_time < min_arrival) min_arrival = p[i].arrival_time;
    if (current_time < min_arrival) current_time = min_arrival;

    // Limit simulation to prevent infinite loops (e.g., 10,000 units)
    while (completed < n && current_time < 10000) {
        int idx = -1;
        int min_rem = INT_MAX;
        
        for (int i = 0; i < n; i++) {
            if (p[i].arrival_time <= current_time && p[i].remaining_time > 0) {
                if (p[i].remaining_time < min_rem) {
                    min_rem = p[i].remaining_time;
                    idx = i;
                }
                else if (p[i].remaining_time == min_rem) {
                    if (idx != -1 && p[i].arrival_time < p[idx].arrival_time) {
                        idx = i;
                    }
                }
            }
        }

        if (idx != -1) {
            p[idx].remaining_time--;
            current_time++;
            if (p[idx].remaining_time == 0) {
                completed++;
                p[idx].completion_time = current_time;
                p[idx].turnaround_time = p[idx].completion_time - p[idx].arrival_time;
                p[idx].waiting_time = p[idx].turnaround_time - p[idx].burst_time;
            }
        } else {
            current_time++;
        }
    }
}

// 4. Round Robin
void calculate_round_robin(Process p[], int n, int quantum) {
    sort_by_arrival(p, n);
    int current_time = 0;
    int completed = 0;
    if (n > 0 && p[0].arrival_time > 0) current_time = p[0].arrival_time;
    for(int i=0; i<n; i++) p[i].remaining_time = p[i].burst_time;

    while (completed < n) {
        int progress = 0;
        for (int i = 0; i < n; i++) {
            if (p[i].arrival_time <= current_time && p[i].remaining_time > 0) {
                progress = 1;
                if (p[i].remaining_time > quantum) {
                    current_time += quantum;
                    p[i].remaining_time -= quantum;
                } else {
                    current_time += p[i].remaining_time;
                    p[i].remaining_time = 0;
                    p[i].completion_time = current_time;
                    p[i].turnaround_time = p[i].completion_time - p[i].arrival_time;
                    p[i].waiting_time = p[i].turnaround_time - p[i].burst_time;
                    completed++;
                }
            }
        }
        if (progress == 0 && completed < n) current_time++;
    }
}