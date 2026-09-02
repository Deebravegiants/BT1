### Title
Webhook shop-domain header is not covered by the HMAC, allowing cross-tenant shop-spoofing on replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then hands the request's `shop` value — read from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header — to the app's handler as the tenant identifier. The HMAC never covers this header, so the binding "HMAC-verified request == shop attributed to it" does not hold.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `Request#shop` is read straight from a header that is excluded from that signable string: [2](#0-1) 

`HmacValidator.validate` only recomputes the HMAC over `verifiable_query.to_signable_string` (i.e., the body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` uses this same validation result to authorize dispatch, then builds `WebhookMetadata` directly from `request.shop` (the unauthenticated header) and hands it to the app's handler: [4](#0-3) 

The binding the gem implicitly claims to provide is:
`HMAC-valid(body, secret) == (topic, body) legitimately originated for shop == request.shop`

In reality the gem only proves `HMAC-valid(body, secret)`; `request.shop` is an unauthenticated, attacker-controllable header value that is never cross-checked against anything in the HMAC-signed body. Any party who is a genuine, unprivileged merchant of the app — and therefore legitimately receives real, correctly-signed webhook deliveries for their *own* shop — can capture one such delivery (raw body + its valid `hmac-sha256` header) and replay the exact same body/HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `Utils::HmacValidator.validate` still succeeds, because it only checks the body, and `Registry.process` still dispatches, delivering `WebhookMetadata` tagged with the victim's shop to the app's handler.

### Impact Explanation
If the host application (as this gem explicitly documents and structures it should) uses `WebhookMetadata#shop` to determine which tenant's records to create/update/delete (the gem's own webhook example/design pattern), this yields cross-tenant data injection: an attacker with only a normal, unprivileged install of the app on their own store can cause webhook-driven side effects (e.g., order/product/customer data writes, uninstall/GDPR-type processing) to be attributed to and applied against a different merchant's tenant data, without ever needing the app's `client_secret`, an access token, or any credential belonging to the victim. This is a cross-tenant access impact, which is explicitly in the Critical impact category for this scan.

### Likelihood Explanation
Likelihood is bounded by the fact that the attacker must already be able to trigger a legitimate webhook delivery for their own shop and capture the raw body + HMAC before replaying it against the target app's endpoint. Both are trivial for any merchant who has installed the app on their own store: they fully control what actions occur in their own store (e.g., updating a product to trigger `products/update`), and they control network egress/observability of requests sent to their own configured callback URL. No secret material or elevated privilege is required — only the attacker's own unprivileged tenant relationship with the app, which matches the "unprivileged internet user" threat model for this scan.

### Recommendation
- Include the shop domain (and ideally the webhook id, to prevent replay) in the HMAC-signed payload verification, or independently verify the shop domain against a value derived from data already bound by the HMAC (e.g., cross-check `request.shop` against a shop identifier embedded in the signed body when available).
- At minimum, document/enforce that `request.shop` must never be trusted as an authenticated tenant identifier by itself; require host applications to correlate the webhook delivery with an existing, previously-authenticated session/shop record (e.g., only accept webhooks for shops that have a currently stored offline session) rather than trusting the header value directly for routing writes.
- Consider binding webhook processing to a per-shop secret or including a nonce/webhook id uniqueness check to prevent simple body/HMAC replay across shops entirely.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` (legitimate, unprivileged action) and configures/observes the webhook callback URL.
2. Attacker performs an action that triggers a real webhook (e.g., updates a product), causing Shopify to POST to the app's endpoint with headers:
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - `x-shopify-hmac-sha256: <valid HMAC over raw body B>`
   - `x-shopify-topic: products/update`
   - body `B`
3. Attacker captures this exact raw body `B` and its valid HMAC header.
4. Attacker replays a new POST to the same app endpoint, keeping body `B` and the `x-shopify-hmac-sha256` value identical, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `B` against the HMAC — this still passes: [5](#0-4) 
6. `WebhookMetadata` is built with `shop: request.shop` = `"victim.myshopify.com"` and passed to the app's handler, which — if it uses `data.shop` to select the tenant to write to, as the gem's design implies — applies data intended for the attacker's own shop against the victim's tenant.

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
