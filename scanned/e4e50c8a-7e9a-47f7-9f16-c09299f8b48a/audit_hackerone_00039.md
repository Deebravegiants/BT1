# [M] Usage of unsafe random function in undici for choosing boundary

## Summary
Severity: Medium (CVSS 6.8)
Program: Node.js
Weakness: Use of Insufficiently Random Values
Reporter: parrot409
State: resolved
Disclosed: 2025-01-23T13:43:08.671Z
CVE: CVE-2025-22150
Source: https://hackerone.com/reports/2913312

## Details
**Summary:** 
[Undici uses Math.random()](https://github.com/nodejs/undici/blob/8b06b8250907d92fead664b3368f1d2aa27c1f35/lib/web/fetch/body.js#L113) to choose the boundary for a `multipart/form-data` request. It is known that the output of `Math.random()` can be predicted if several of its generated values are known.

**Description:** 
If an attacker can access a few generated values of `Math.random()` and has control over one of the fields of a multipart request, they can add or overwrite fields that are not meant to be controllable.

If there is a mechanism in an app that sends multipart requests to an attacker-controlled website, they can use this to leak the necessary values.

Here is an example app that is vulnerable to this bug.
```javascript
#!/usr/bin/env node
const express = require('express')

const BACKEND_API = 'http://localhost:2000/order.php'

const app = express()

app.use(express.urlencoded({ extended: false }))

app.get('/trigger-webhook',(req,res)=>{
	let url = req.query.url
	let data = new FormData()
	data.append('event','example-event')
	fetch(url,{
		body: data,
		method: 'POST'
	})
	res.send('OK')
})

app.post('/order',(req,res)=>{
	let description = req.body.description || 'Please wrap it in Christmas-themed wrapping paper.'
	let data = new FormData()
	data.append('price','4000')
	data.append('customer_id','1')
	data.append('item_id','1')
	data.append('description',description)
	fetch(BACKEND_API,{
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/2913312_
