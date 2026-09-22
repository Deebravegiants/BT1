# [H] CVE-2021-47391

## Summary
Severity: High
Advisory: CVE-2021-47391
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47391
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/cma: Ensure rdma_addr_cancel() happens before issuing more requests

The FSM can run in a circle allowing rdma_resolve_ip() to be called twice
on the same id_priv. While this cannot happen without going through the
work, it violates the invariant that the same address resolution
background request cannot be active twice.

       CPU 1                                  CPU 2

rdma_resolve_addr():
  RDMA_CM_IDLE -> RDMA_CM_ADDR_QUERY
  rdma_resolve_ip(addr_handler)  #1

			 process_one_req(): for #1
                          addr_handler():
                            RDMA_CM_ADDR_QUERY -> RDMA_CM_ADDR_BOUND
                            mutex_unlock(&id_priv->handler_mutex);
                            [.. handler still running ..]

rdma_resolve_addr():
  RDMA_CM_ADDR_BOUND -> RDMA_CM_ADDR_QUERY
  rdma_resolve_ip(addr_handler)
    !! two requests are now on the req_list

rdma_destroy_id():
 destroy_id_handler_unlock():
  _destroy_id():
   cma_cancel_operation():
    rdma_addr_cancel()

                          // process_one_req() self removes it
		          spin_lock_bh(&lock);
                           cancel_delayed_work(&req->work);
	                   if (!list_empty(&req->list)) == true

      ! rdma_addr_cancel() returns after process_on_req #1 is done

   kfree(id_priv)

			 process_one_req(): for #2
                          addr_handler():
	                    mutex_lock(&id_priv->handler_mutex);
                            !! Use after free on id_priv

rdma_addr_cancel() expects there to be one req on the list and only
cancels the first one. The self-removal behavior of the work only happens
after the handler has returned. This yields a situations where the
req_list can have two reqs for the same "handle" but rdma_addr_cancel()
only cancels the first one.

The second req remains active beyond rdma_destroy_id() and will
use-after-free id_priv once it inevitably triggers.

Fix this by remembering if the id_priv has called rdma_resolve_ip() and
always cancel before calling it again. This ensures the req_list never
gets more than one item in it and doesn't cost anything in the normal flow
that never uses this strange error path.

## References
- https://git.kernel.org/stable/c/9a085fa9b7d644a234465091e038c1911e1a4f2a
- https://git.kernel.org/stable/c/03d884671572af8bcfbc9e63944c1021efce7589
- https://git.kernel.org/stable/c/305d568b72f17f674155a2a8275f865f207b3808
