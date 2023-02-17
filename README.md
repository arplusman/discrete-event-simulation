# Discrete Event Simulation
2
This project is a simulation of a discrete-event system that is contained of some servers and some incoming tasks. There are some processor servers that are ready to serve. each server has a number of core processors that work with a certain speed. In this system, tasks can have different types that enter the system with different rates. each task enters a scheduler server at first, and this server specefies that each task should be processed by which server. All tasks have a deadline that determines their maximum waiting time untill being processed by a server. If we pass the deadline of a task but it is still in a waiting queue, that task will leave the queue. None of the queues have capacity limit. A sample of this system that contains 3 processor servers is showed below:
<p align="center">
<img width="678" alt="Screenshot 1401-11-28 at 10 52 29 PM" src="https://user-images.githubusercontent.com/45389988/219783564-65a116a6-2623-4945-86ce-494911c591bd.png">
</p>


## Task Types
In this system, we have two kinds of tasks, named tasks type 1 and tasks type 2. Priority of tasks 1 is alaways higher than the priority of task 2, and among tasks of the same type, priority is based on the entering time in the system. All tasks enter the system following poisson distibution with rate $\lambda$. On average, 10 percent of the tasks are type 1 and 90 percent of them are type 2. A task can reach its deadline and become expired when waiting if scheduler queue or any of server queues. deadlines of tasks follow an exponential distribution with mean of $\alpha$.

## Scheduler
Scheduler has one queue and one core.(_M/M/1_) Scheduler is not idle unless its queue is empty. Scheduler, if a task exists, pop a task from the start of the queue and sends it to the server queue whit minimum length. If there are more than one server queue with minimum queue, scheduler choose among them randomly. Scheduler serving time for each task follows poisson distibution with rate $\mu$.

## Processor Servers
Every processor server has one queue with several cores. a core is not idle unless its server queue is empty. Every core has its own serving time which follows exponential distribution with specified mean. 

## Configuratoins
Numebr of Server and number of cores of each server in this system are 5 and 3, respectively.

## Inputs
Input of the program includes 6 line which should follow this format:
- First line includes parameters $\lambda$, $\alpha$, and $\mu$
- each of the next 5 lines includes 3 numbers which specifies mean of serving time of cores of each server.

## Outputs
Output for this simulation which simulates the system for 1 Million tasks should contain these values:
1. Mean of spent time for each task in system at all and for each task type seperately.
2. Mean of waiting time in queues for each at at all and for each task type seperately.
3. percent of expired tasks at all and for each taks type seperately.
4. Mean of length of every queue in the system.
