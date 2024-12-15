

const axios = require('axios');
const  asista_Objects = require("./utils.js")

exports.handler = async (event) => {
    console.log("Event:", event);

    
    let res
 
    function extractThresholdValue(inputString) {
        const regex = /Threshold Crossed: .+threshold \((\d+\.\d+)\)/;
        const match = inputString.match(regex);
        if (match && match.length > 1) {
            return parseFloat(match[1]);
        } else {
            return null;
        }
    }
 
    function convertUTCToIST(utcDate) {
        const date = new Date(utcDate);
        return date.toLocaleString('en-US', { timeZone: 'Asia/Kolkata' });
    }
 
 
    //Ticket Creation function
    async function createTicket(ticketData) {
 
        try {
            const response = await axios.post(
                asista_Objects.asistaTenetURL+"/servicedesk/api/v1/requests",
                {
                    "subject": ticketData.message,
                    "description": `${ticketData.message} on ${ticketData.time}`,
                    "requestType": 31,
                    "priority":ticketData.priority,
                    "email": asista_Objects.email,
                    "username": asista_Objects.username,
                    "externalRef": ticketData.uid,
                    "custom": [],
                    "itemRefType": ticketData.itemRefType,
                    "itemRefId": ticketData.itemRefId
                },
                {
                    headers: {
                        "Content-Type": "application/json",
                        "X-App-Key": asista_Objects["X-App-Key"],
                        "X-App-Secret": asista_Objects["X-App-Secret"]
                    }
                }
            );

 
 
            // Process the response as needed
            console.log({ "response": response.data });
            return  {
                status: 200,
                body: { "Message": "New Request Created", "TicketData": response.data, "UID" :ticketData.uid  }
            };
        } catch (error) {
            console.log("Error:", error);
            return  {
                status: 200,
                body: { "Message": "Error occurred while calling Asista API", "error": error }
            };
        }
    }
 
    // If condition only work if data contains site check
    if (event.type && event.type == "site-check")
    {
    var DateTime = new Date()    
    console.log(DateTime)
    
    let SiteTicketdata = {
        message: `${event.website} site check failed ` ,
        time: `${convertUTCToIST(DateTime)} | status code ${event.statuscode}`,
        uid: `${event.website}failed`,
        priority: event.sitePriority
        // itemRefType: asista_Objects["aws-itemRefType"] -- For asset mapping
    }
    console.log(SiteTicketdata)
    
    
    let dataree = await createTicket(SiteTicketdata)
    }
    
    
    
    
    
    // Else part only work if the data does not contains site check
    

};