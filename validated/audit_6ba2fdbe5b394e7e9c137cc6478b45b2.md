## Title
Webhook HMAC signature does not cover the `shop-domain` header, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw webhook body, so the HMAC signature validated by `Utils::HmacValidator` binds nothing but the payload bytes. The `shop` value used to route/attribute the webhook to a specific merchant is read from the `x-shopify-shop-domain` (or `shopify-shop-domain`) header, which is never part of the signed material. This breaks the identity binding `shop authenticated == shop the payload is attributed to`, letting a party that possesses one valid `(body, hmac)` pair (e.g. from webhooks fired for their own installed shop) replay it with a forged `shop-domain` header pointing at a different, victim shop.

### Finding Description
The signable string for a webhook request is defined as just the raw body: [1](#0-0) 

`shop` is read from an independent, unsigned header: [2](#0-1) 

`HmacValidator.validate` computes the HMAC purely from `to_signable_string`, i.e. only the body: [3](#0-2) 

`Registry.process` accepts the request once the (body-only) HMAC check passes, then forwards the header-derived, unauthenticated `shop` value straight to the app's handler as the tenant identity for the event: [4](#0-3) 

The `api_secret_key` used for HMAC computation is a single app-level secret shared across every shop that installs the app — it is not per-shop. Consequently, an unprivileged user who installs the app on their own store, and then triggers a real Shopify webhook, obtains a valid `(raw_body, hmac)` pair signed with the app's shared secret. Because the `shop-domain` header is outside the signed material, that same `(raw_body, hmac)` pair remains valid if replayed to the app's webhook endpoint with the `x-shopify-shop-domain` header changed to any other shop's domain. The equality the code implicitly (and incorrectly) assumes is:

`HMAC-verified(body) == HMAC-verified(shop, body)`

but only the left side is actually checked, while the right side (the `shop` claim actually consumed by the handler) is fully attacker-controlled.

### Impact Explanation
This allows cross-tenant confusion/attack: a malicious app-installer can forge webhook deliveries "from" any other merchant shop that also uses the same app, attributing attacker-chosen (but real, validly-HMAC'd) payload content to a victim shop. Depending on how the hosting app's `WebhookHandler` uses `data.shop` (e.g., to look up/update per-shop state, trigger `app/uninstalled` cleanup, disable billing, or mutate merchant records keyed by shop domain), this can lead to state corruption or actions being taken against a shop the attacker doesn't control — a cross-tenant impact within the scope of this gem's own webhook-processing logic.

### Likelihood Explanation
Exploitation requires the attacker to be able to (a) install the app on a shop they control to obtain a legitimately-signed `(body, hmac)` pair, and (b) send arbitrary HTTP requests (with attacker-chosen headers) directly to the app's public webhook endpoint. Both conditions are realistic for any "unprivileged internet user" scenario involving a public app with an open webhook receiver, since nothing in this gem prevents header spoofing — the gem's own validation logic (`HmacValidator`) does not include the shop identity in the signed bytes.

### Recommendation
Extend `Webhooks::Request#to_signable_string` (or add a secondary check in `Registry.process`) so the `shop` (and ideally `topic`/`webhook-id`) are cryptographically bound to the signature, not merely read from unauthenticated headers, e.g. by verifying that the resolved shop matches the identity the hosting application already possesses for that HMAC-verified body (or by incorporating the shop domain into the signable string, if this can be done compatibly with Shopify's signing scheme).

### Proof of Concept
1. Attacker installs the target app onto their own shop `attacker.myshopify.com`, generating a real webhook delivery with body `B` and header `x-shopify-hmac-sha256: H` (H = HMAC-SHA256(app_secret, B)), as validated in: [5](#0-4) 
2. Attacker captures `B` and `H` from this legitimate delivery.
3. Attacker sends a POST directly to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged, still valid because it only signs `B`), but `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` succeeds (it only checks `B` against `H`), and `Registry.process` invokes the handler with `shop: "victim-shop.myshopify.com"`: [6](#0-5) 
5. The hosting application processes attacker-controlled webhook content as if it originated from the victim shop.

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
