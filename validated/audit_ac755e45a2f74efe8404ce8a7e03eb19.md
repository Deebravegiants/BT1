### Title
Webhook `shop` identity is not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by HMAC-validating the raw request body, but the `shop` identity that is handed to the app's webhook handler is read from an HTTP header that is excluded from that signature. Any party able to deliver an HTTP request to the app's webhook endpoint can therefore keep a legitimately-signed body/HMAC pair (obtainable from their own, attacker-controlled shop installation) while swapping the `shop-domain` header to point at a victim shop, and the gem will accept it as authentic.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `Webhooks::Request#shop` is pulled straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never mixed into `to_signable_string`: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the `hmac` field against exactly that signable string (the body bytes) using the app's shared `api_secret_key`: [3](#0-2) 

`Registry.process` gates only on this HMAC check, then forwards the *unauthenticated* `request.shop` value straight into the tenant-identifying `WebhookMetadata` passed to the app's handler: [4](#0-3) 

The identity binding that should hold is: `hmac-verified bytes == bytes the shop identity is derived from`. Here it does not — the bytes verified by HMAC (`raw_body`) and the bytes the shop/tenant identity is parsed from (the `shop-domain` header) are disjoint. Because the `api_secret_key`/`client_secret` used to compute the HMAC is the same for every shop that installs a given app, any unprivileged user who has legitimately installed the app on their own store can capture one valid `(raw_body, hmac)` pair from a webhook Shopify sends them, then replay it to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` still passes (body/HMAC unchanged), so `Registry.process` dispatches the handler with `shop: <victim-shop>`, causing the host application to act as if the event came from the victim tenant.

### Impact Explanation
This breaks the tenant boundary the gem is meant to enforce for webhook processing: an attacker with only their own low-privilege app installation can make the library present attacker-controlled event data as originating from an arbitrary victim shop. Depending on how the consuming app keys session lookups, data-redaction, or business logic off `WebhookMetadata#shop` (as intended and documented usage of this API), this enables cross-tenant data confusion/access — e.g. triggering `shop/redact` or `customers/redact` style logic, or any handler logic keyed by shop, against a shop the attacker does not own. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
The only prerequisite is the ability to install the target app on any shop the attacker controls (the normal way any merchant/developer can) so as to receive one real, validly-signed webhook, and the ability to send an arbitrary HTTP request with custom headers to the app's public webhook endpoint. No access token, `client_secret`, or privileged account for the *victim* is required — only the attacker's own legitimate, unprivileged installation. This is straightforward to execute and does not depend on any host-application misuse; it stems directly from `Webhooks::Request`/`Registry.process` in this gem trusting an unsigned header for identity.

### Recommendation
Bind the shop identity into the verified material, e.g. by including the `shop-domain` (and ideally `topic`, `webhook-id`) header value in `to_signable_string`, or otherwise cryptographically deriving/checking the shop against data verified from the signed body/registered app installation, before it is ever exposed to consumers as `request.shop` or placed into `WebhookMetadata`. At minimum, document/enforce that callers must independently confirm the `shop` belongs to an installation they expect, and consider validating that the shop domain header is one for which the app currently holds an active session before dispatching.

### Proof of Concept
1. Install the target Shopify app on `attacker-shop.myshopify.com` (a normal, unprivileged action).
2. Trigger any subscribed webhook topic (e.g. `orders/create`) on that shop and capture the raw POST body `B` and the `X-Shopify-Hmac-Sha256` header `H` that Shopify sends — `H` is a valid HMAC of `B` under the app's `client_secret`.
3. Replay a new HTTP request to the app's webhook endpoint using the exact same body `B` and header `H`, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and any desired `X-Shopify-Topic`/`X-Shopify-Webhook-Id`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`= B`) and finds it matches `H` — validation passes.
5. `Registry.process` then invokes the registered handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)`, so the app processes attacker-supplied data as if it were an authentic event from `victim-shop.myshopify.com`. [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
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
