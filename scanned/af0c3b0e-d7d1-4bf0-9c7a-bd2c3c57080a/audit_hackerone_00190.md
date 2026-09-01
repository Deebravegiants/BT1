# [M] Null Pointer Dereference in PHP Session Upload Progress

## Summary
Severity: Medium
Program: Internet Bug Bounty
Weakness: NULL Pointer Dereference
Reporter: ryat
State: resolved
Disclosed: 2020-11-09T01:47:56.522Z
Source: https://hackerone.com/reports/798744

## Details
Affected Versions
------------
Affected is all of PHP5.4/5.5/5.6
Affected is all of PHP7

Credits
------------
This vulnerability was disclosed by Taoguang Chen.

Description
------------
session.c
```
static int php_session_rfc1867_callback(unsigned int event, void *event_data, void **extra) /* {{{ */
{
	...
	switch(event) {
		case MULTIPART_EVENT_START: {
			multipart_event_start *data = (multipart_event_start *) event_data;
			progress = ecalloc(1, sizeof(php_session_rfc1867_progress));  <=== the progress was allocated and initialized with zeros.
			progress->content_length = data->content_length;
			progress->sname_len  = strlen(PS(session_name));
			PS(rfc1867_progress) = progress;
		}
		break;
		case MULTIPART_EVENT_FILE_START: {
			...
			if (Z_ISUNDEF(progress->data)) {
                ...
				array_init(&progress->data); <=== if goto MULTIPART_EVENT_FILE_START, &progress->data will be initialized with array-type ZVAL.
				...
			}
            ...
        }
        break;
		...
		case MULTIPART_EVENT_END: {
			multipart_event_end *data = (multipart_event_end *) event_data;
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/798744_
