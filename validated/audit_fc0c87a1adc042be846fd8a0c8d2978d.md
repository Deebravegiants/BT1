### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `api_version`, and `webhook_id` from unauthenticated HTTP headers, but the HMAC signature that `Utils::HmacValidator.validate` checks is computed only over the raw request body. An attacker who owns any shop with the app installed can capture a legitimate webhook (body + valid `x-shopify-hmac-sha256`) sent to their own tenant and replay it to the app's webhook endpoint with a forged `x-shopify-shop-domain` header naming a different, victim shop. The HMAC check still passes (it only verifies the body bytes), and the handler receives `WebhookMetadata` believing the event belongs to the victim tenant.

### Finding Description
`Utils::HmacValidator.validate` computes and compares the signature only over `verifiable_query.to_signable_string`. For webhook requests, `Request#to_signable_string` returns solely `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from caller-supplied headers with no cryptographic binding to the signed body: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` (and `request.topic`) to route and label the event without any additional binding check: [3](#0-2) 

This exactly matches the "field acted on but not covered by the HMAC" analog: the identity binding that should hold is `hmac_signed_bytes == bytes_the_handler_trusts_for_tenant_identity`, but in reality `hmac_signed_bytes == raw_body_only` while `tenant_identity_used_by_handler == shop_domain_header` (unsigned). Any attacker who can obtain one valid `(raw_body, hmac)` pair — trivially available to them as the legitimate recipient of their own shop's webhooks — can swap the `shop-domain` header and produce a request that passes HMAC validation while asserting an arbitrary victim shop.

### Impact Explanation
This breaks the tenant-isolation invariant that a webhook's HMAC guarantees it genuinely originates for the shop attributed to it. Host applications that rely on `WebhookMetadata#shop` from a Registry handler (as illustrated by the gem's documented API surface) to select which merchant's records to update, delete, or notify — a common pattern in Shopify apps — can be tricked into performing actions attributed to or targeting a merchant tenant the attacker does not control. This is a cross-tenant integrity issue reachable purely from an unprivileged internet-connected shop, satisfying the "cross-tenant access" Critical category.

### Likelihood Explanation
Likelihood is high for any attacker who has legitimately installed the app on at least one shop (a standard, unprivileged action): they naturally receive real webhooks with valid HMACs for their own shop and can freely replay the exact same bytes to the endpoint with a modified `shop-domain` header, since nothing in the gem ties the header to the signed payload.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-signed material, or require callers of `Registry.process` to independently verify `request.shop` against the shop associated with the session/subscription that is expected to receive that webhook before trusting `WebhookMetadata#shop`. At minimum, document and enforce that `shop` must be validated against a known/registered shop list bound to the signature, mirroring the OAuth `AuthQuery` pattern where all identity-bearing parameters are part of `to_signable_string`.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B`), header `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the identical `B` and `H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (`= B`) only — validation succeeds.
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed_body, ...)`, causing the host application to act as if the event pertains to `victim-shop.myshopify.com` even though it never sent this data.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```
