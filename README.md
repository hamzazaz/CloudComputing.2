# Event-Driven Order Notification System Using AWS

This document outlines the process I followed to build an event-driven architecture for an e-commerce platform using AWS services. The architecture involves:

- **Amazon SNS** for broadcasting notifications
- **Amazon SQS** for queuing order events
- **AWS Lambda** to process messages
- **Amazon DynamoDB** to store order data

---

## Tools Used

- **Amazon SNS**: For broadcasting notifications to all subscribed endpoints.
- **Amazon SQS**: For queuing the order events and ensuring they are processed reliably.
- **AWS Lambda**: For processing the messages and performing operations like logging and storing data.
- **Amazon DynamoDB**: For storing order data with fast, reliable, and scalable access.

---

## Step 1: DynamoDB Setup

I began by creating a **DynamoDB table** named `Orders` with the following configuration:

- **Partition Key**: `orderId` (String)
- **Attributes**:
  - `userId` (String)
  - `itemName` (String)
  - `quantity` (Number)
  - `status` (String)
  - `timestamp` (String)

After creating the table, I checked its status to ensure it was marked as **Active**. I also verified that I had the correct permissions to read and write from this table using the Lambda execution role.

---

## Step 2: SNS Topic Creation

I created an **SNS topic** named `OrderTopic` to broadcast the order notifications.

- **Topic Type**: Standard
- **Topic Name**: `OrderTopic`

After the topic was created, I copied the **Topic ARN**, which would be used later for subscribing the SQS queue to this SNS topic.

---

## Step 3: SQS Queue Creation

I set up an **SQS Standard queue** named `OrderQueue` to queue messages before they are processed by the Lambda function. To ensure reliable message handling, I also configured a **Dead Letter Queue (DLQ)**. Here’s how I set it up:

1. **Created DLQ**:
   - **Queue Name**: `OrderDLQ`

2. **Created Main Queue**:
   - **Queue Name**: `OrderQueue`
   - **DLQ Configuration**: Enabled with a reference to the `OrderDLQ`
   - **Max Receive Count**: Set to 3 to ensure messages are retried up to 3 times before being sent to the DLQ.

3. **Subscribed `OrderQueue` to the `OrderTopic` SNS topic**: This ensures that any message published to `OrderTopic` is routed to the queue for processing.

Once I set up the queue and subscriptions, I tested it by publishing a simple message to ensure it was successfully routed to the `OrderQueue`.

---

## Step 4: Lambda Function Permissions

Before setting up the **Lambda function**, I made sure the Lambda execution role had the proper permissions. Specifically, I attached the following policies to allow Lambda to interact with DynamoDB and SQS:

- **AmazonDynamoDBFullAccess** (for accessing DynamoDB)
- **AmazonSQSFullAccess** (for accessing SQS)

I added these permissions by navigating to **IAM → Roles**, selecting the Lambda execution role, and then attaching the necessary policies.

---

## Step 5: Lambda Function Setup

I created a **Lambda function** named `ProcessOrderFunction` with Python 3.12 as the runtime. The function was configured to trigger whenever a new message was added to the `OrderQueue` SQS queue.

### Lambda Function Code Behavior

- **Message Parsing**: The Lambda function processes incoming messages, extracting order details (e.g., `orderId`, `userId`, `itemName`, etc.).
- **Logging**: It logs each order, helping in debugging and monitoring.
- **Data Insertion**: The Lambda function stores the parsed order details into the DynamoDB `Orders` table.

I deployed the Lambda function and verified its connection to the `OrderQueue` and DynamoDB.

---

## Step 6: Testing the Flow

I tested the full system by publishing a test message to the **OrderTopic SNS topic**. Below is the JSON format for the test message:

```json
{
  "orderId": "O1234",
  "userId": "U123",
  "itemName": "Laptop",
  "quantity": 1,
  "status": "new",
  "timestamp": "2025-05-03T12:00:00Z"
}
```
After publishing the message, I confirmed that it appeared in the OrderQueue.
I then checked the Lambda logs to ensure that the order was processed correctly.
Finally, I went to the DynamoDB Orders table and verified that the new order was stored as expected.
