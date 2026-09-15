# [C] Broken Authorization Scheme

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description
Anyone can enumerate all tickets belonging to any wallet address by providing the corresponding address key (SHA256 of the address) to the right API endpoint. Users can also create tickets on behalf of other users by sending a POST request to the API with the corresponding address key. Finally, any user can view and post updates to tickets belonging to other users by injecting arbitrary ticket IDs in GET/POST requests sent to the API. The root cause is that the ticket IDs and address keys are not authenticated against a particular user ID/access token. Thus, it allows unauthorized access to potentially sensitive ticket information and the ability to impersonate users and create tickets and post comments to tickets belonging to other users. This is a critical flaw which must be fixed.

#### Examples


**packages/snap/utils/backend_functions.ts:L5-L17**
```solidity
export async function create_ticket(req_address: string, title: any, description: any, apikey: any) {

    const address_key = SHA256(req_address, { outputLength: 32 }).toString();

    try{
        const requester = "userbot@consensys.net";
        const ticketData = {ticket: {
            subject: title,
            requester: requester,
            tags: 'anon_' + address_key, 
            comment:{body: description }
        }};
        const url = 'https://71z6182pq3.execute-api.eu-west-1.amazonaws.com/default/tickets?create=true';
```


**packages/snap/utils/backend_functions.ts:L38-L42**
```solidity
const address_key = SHA256(req_address, { outputLength: 32 }).toString();

try{
    const url = 'https://71z6182pq3.execute-api.eu-west-1.amazonaws.com/default/tickets';
    const final_url = url + '?address=' + address_key;
```


**packages/snap/utils/backend_functions.ts:L67-L72**
```solidity
export async function get_ticket_comments(ticket_id : any, req_address: any, apikey: any){
    let json_ticket_comments = null;
    const address_key = SHA256(req_address, { outputLength: 32 }).toString();

    try{
        const url = 'https://71z6182pq3.execute-api.eu-west-1.amazonaws.com/default/tickets?ticketId=' + ticket_id;
```


**packages/snap/utils/backend_functions.ts:L94-L100**
```solidity
export async function update_ticket(ticket_id: any, input_data: any, req_address: any, apikey: any) {
    console.log(`Updating ticket ${ticket_id} with comment: `, input_data);
    const address_key = SHA256(req_address, { outputLength: 32 }).toString();

    try {
        const url = 'https://71z6182pq3.execute-api.eu-west-1.amazonaws.com/default/tickets?ticketId='
            + ticket_id + '&create=false' + '&from_snap';
```

#### Recommendation
Implement strict validation and proper access control mechanisms to ensure that users can only create, view and modify tickets they are authorized to access. This could involve verifying user permissions against the ticket ID and address key before granting access or allowing modifications.
