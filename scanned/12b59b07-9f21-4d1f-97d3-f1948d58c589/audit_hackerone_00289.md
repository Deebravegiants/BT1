# [M] Invalid read when wddx decodes empty boolean element

## Summary
Severity: Medium
Program: Internet Bug Bounty
Weakness: Memory Corruption - Generic
Reporter: fosec
State: resolved
Disclosed: 2019-11-12T09:20:07.865Z
Source: https://hackerone.com/reports/188661

## Details
Description
-----------
I have found some vulnerable code in wddx extension. The trouble happens when trying to process 'boolean' tag. If I open <boolean> tag without data, new st_entry item WILL NOT be pushed into stack. When <boolean> tag is closed and stack->top is greater than 1, st_entry item at top of stack WILL be popped out of stack.

Look at following snip code, a new st_entry will be pushed into stack if atts is not NULL. If I open <boolean> tag by using '<boolean/>', 'atts' is NULL.

``` c
static void php_wddx_push_element(void *user_data, const XML_Char *name, const XML_Char **atts)
{
	.....
	} else if (!strcmp((char *)name, EL_BOOLEAN)) {
		int i;

		if (atts) for (i = 0; atts[i]; i++) {
			if (!strcmp((char *)atts[i], EL_VALUE) && atts[i+1] && atts[i+1][0]) {
				ent.type = ST_BOOLEAN;
				SET_STACK_VARNAME;

				ZVAL_TRUE(&ent.data);
				wddx_stack_push((wddx_stack *)stack, &ent, sizeof(st_entry));
				php_wddx_process_data(user_data, atts[i+1], strlen((char *)atts[i+1]));
				break;
			}
		}
	} 
    .....
}
```

Look at the other snip code, I see "boolean" tag is popped and freed without checking anything:

``` c
static void php_wddx_pop_element(void *user_data, const XML_Char *name)
{
	st_entry 			*ent1, *ent2;
	wddx_stack 			*stack = (wddx_stack *)user_data;


```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/188661_
