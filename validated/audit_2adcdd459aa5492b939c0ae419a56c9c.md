### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC computed over the raw request body, then trusts the `shop` (and `topic`/`webhook_id`) values taken from unauthenticated HTTP headers to build the `WebhookMetadata` passed to the app's handler. Because the tenant-identifying field (`shop`) is not part of the HMAC-signed content, any party who can obtain one valid `(body, hmac)` pair for their own shop can replay it against the app's webhook endpoint while spoofing the `shop-domain` header to a victim shop, producing a webhook the app will process as if it genuinely originated from the victim tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from request headers with no cryptographic binding to the HMAC: [2](#0-1) 

`Utils::HmacValidator.validate` computes `HMAC(secret, to_signable_string)` and compares it to the `hmac` header — i.e. it only proves that the *body bytes* were signed by an entity holding `api_secret_key`; it says nothing about which shop the body belongs to: [3](#0-2) 

`Registry.process` uses exactly this check and then forwards the unauthenticated `request.shop` straight into the handler's `WebhookMetadata`: [4](#0-3) 

The identity binding that should hold is:
`shop bound by HMAC == shop delivered to app handler`

but the actual binding enforced by this code is:
`HMAC(secret, body) valid` AND `shop == header value (unauthenticated)`

Since the same app's webhook endpoint is shared across every shop that installs it, and a merchant of that app can legitimately generate real, correctly-signed webhooks for their own store (e.g., by triggering `orders/create` in their own dev/production shop), that merchant can capture the genuine `(raw_body, x-shopify-hmac-sha256)` pair from a webhook Shopify delivers to their own endpoint, then POST the same body/HMAC to the shared app webhook URL while substituting `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) with a victim shop's domain. `Utils::HmacValidator.validate` still succeeds because it only checks the body, so `Registry.process` dispatches the handler with `shop: <victim shop>` and attacker-chosen body content.

### Impact Explanation
This breaks tenant isolation: an unprivileged user who merely operates their own store using the same app can forge webhook events attributed to a different merchant's shop, with a body of their choosing (subject to it being a body they can get legitimately signed for their own shop, or any topic they can trigger). Depending on the app's handler logic keyed off `data.shop`, this enables cross-tenant data injection/forgery (e.g., fabricated orders, fake `app/uninstalled` triggering deletion of the victim's stored session/access token, or other shop-scoped side effects) — a cross-tenant access impact.

### Likelihood Explanation
Exploitation only requires the attacker to run their own free/dev shop that installs the target app (a standard, unprivileged capability), capture one legitimate webhook delivery to their own endpoint, and re-POST it with a modified `shop-domain` header to the app's public webhook URL. No access token, `client_secret`, or privileged account is needed, making this practically reachable by any internet user who can install the app.

### Recommendation
Bind the tenant identity into the signed material, or otherwise cryptographically tie the `shop` header to the payload before trusting it:
- Include the `shop`/`topic`/`webhook_id` headers (or at minimum `shop`) in `to_signable_string` so the HMAC covers them, and reject requests where the signed shop doesn't match the header, or
- Cross-check `request.shop` against an independently-verified source (e.g., the shop associated with the already-stored session/access token) before dispatching to the handler, rejecting mismatches.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Attacker triggers a webhook event (e.g. updates an order) and captures the raw POST body `B` and header `x-shopify-hmac-sha256: H` that Shopify sends to the app's webhook endpoint for `attacker.myshopify.com`.
3. Attacker sends a new HTTP POST to the same app webhook URL with:
   - Body: `B` (unchanged)
   - Header `x-shopify-hmac-sha256: H` (unchanged)
   - Header `x-shopify-shop-domain: victim-shop.myshopify.com` (spoofed)
   - Header `x-shopify-topic`, `x-shopify-webhook-id` as desired
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which recomputes `HMAC(secret, B)` and matches `H` — validation passes. [4](#0-3) 
5. The handler is invoked with `WebhookMetadata` whose `shop` is `victim-shop.myshopify.com` even though the body/topic were never associated with that shop by Shopify — a cross-tenant identity confusion the app cannot detect from within this gem's API.

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
