### Title
Webhook `shop` (and `topic`) identity fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the `shop` (and `topic`) values taken from HTTP headers that are never included in that signature, and hands them to the app's `WebhookHandler` as the tenant identity for the event.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes/compares the HMAC exclusively against `verifiable_query.to_signable_string` (i.e., the body), never the headers: [2](#0-1) 

`Registry.process` accepts the request once `HmacValidator.validate` passes, and then builds `WebhookMetadata` using `request.shop` and `request.topic`, both of which are read straight from HTTP headers (`shop-domain`, `topic`) with no cryptographic binding to the signed body: [3](#0-2) [4](#0-3) 

The identity equality the gem should enforce is: `shop_bound_by_HMAC(raw_body) == shop_used_for_tenant_routing(header)`. Because only the body bytes are signed, an attacker who can trigger a legitimately-signed webhook for their own shop (e.g., by performing an action in their own store that Shopify will webhook about, which they fully control since Shopify signs with the app's `api_secret_key` on Shopify's side and delivers it over HTTP to the app's public endpoint) obtains a `(raw_body, valid_hmac)` pair. They can then replay that exact body+HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header (and/or `X-Shopify-Topic`) with a victim shop's domain. `HmacValidator.validate` still succeeds because it only checks the untouched body against the secret, while `Registry.process` reports the event to the handler as coming from the victim shop.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook consumers: an app author cannot trust `WebhookMetadata#shop` to identify which merchant's data the event body pertains to, even though the API's documented contract implies the HMAC authenticates the whole webhook delivery. Any host application that uses `data.shop` to look up per-tenant session/state (a documented, expected use per `docs/usage/webhooks.md`) can be induced to apply attacker-supplied body content under a different tenant's identity — a cross-tenant integrity issue reachable purely from the public internet without credentials, matching the "shop authenticated versus shop used for tenant identity" binding break class.

### Likelihood Explanation
Webhook endpoints are unauthenticated public HTTP endpoints by design (that's the entire point of HMAC-based webhook verification), so any unprivileged internet user who can obtain one valid `(body, hmac)` pair — trivially, by owning/operating their own Shopify dev store and installing the target app — can replay it with an arbitrary `shop-domain` header value. No secret, token, or privileged access is required.

### Recommendation
Include the `shop` (and ideally `topic`, `webhook-id`, `api-version`) header values in the signable payload used for HMAC verification (e.g., mirror Shopify's guidance which signs the raw request body but also requires the app to independently trust `X-Shopify-Shop-Domain` only for installed/known shops, or better, bind these header values into `to_signable_string`/validation), and reject webhooks whose `shop` header does not correspond to a shop the app knows/trusts before dispatching to handlers.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and triggers an event (e.g., `orders/create`) — Shopify sends a webhook with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(secret, B)`.
2. Attacker POSTs the identical body `B` and signature `H` to the app's webhook endpoint but changes `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) recomputes `HMAC-SHA256(secret, B)` and finds it equal to `H`, so validation passes.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: B, ...)`, even though `B` actually originated from the attacker's own shop — the app processes attacker-controlled data under the victim tenant's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```
