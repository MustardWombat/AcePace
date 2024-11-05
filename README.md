+----------------------------+
|       Flask Server         |
+----------------------------+
             |
             v
+----------------------------+
| Environment & API Setup    |
+----------------------------+
   |         |           |
   v         v           v
Load     Set secret   OpenAI API 
.env      key         Key
variables   
             |
             v
+----------------------------+
|       Core Functions       |
+----------------------------+
| 1. calculate_final_score() |
| 2. generate_quiz()         |
| 3. get_question()          |
| 4. submit_answer()         |
| 5. get_score_summary()     |
+----------------------------+
             |
             v
+----------------------------+
|      Routes / Endpoints    |
+----------------------------+
| /generate_quiz (POST)      |
| /get_question (GET)        |
| /submit_answer (POST)      |
| /get_score_summary (GET)   |
| /                          |
+----------------------------+
             |
             v
+----------------------------+
|     Session Management     |
+----------------------------+
| Track quiz questions,      |
| question index, and scores |
+----------------------------+
             |
             v
+----------------------------+
|     CSV File Operations    |
+----------------------------+
| Append answers & results   |
| for scoring persistence    |
+----------------------------+
