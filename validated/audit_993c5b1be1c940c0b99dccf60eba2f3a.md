This confirms `Context.api_secret_key` is a single, global secret shared across **all** shops that install the app [1](#0-0) , and there is no per-shop secret used to validate webhooks.

### Title
Webhook `shop` domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signable string from the raw request body only, while the `shop` (and `topic`/`webhook_id`) values are read from unauthenticated HTTP headers. Since every shop installed on an app shares the same `Context.api_secret_key`, an attacker who controls one legitimate tenant (their own installed shop) can obtain a valid `(body, hmac)` pair and replay it to the app's webhook endpoint with a forged `shop-domain` header pointing at a victim shop. `HmacValidator` only re-derives the signature from the body, so it will accept the forged request, and `Registry.process` will hand the attacker-chosen `shop` value straight to the app's handler as if Shopify had confirmed it.

### Finding Description
The HMAC-validated field set for a webhook request excludes the shop identity: [2](#0-1) 

`to_signable_string` returns only `@raw_body`, never the `shop`, `topic`, or `webhook_id` headers, so those headers are outside the authenticated envelope. `HmacValidator.validate` computes the expected signature purely from `to_signable_string` and compares it to the received HMAC: [3](#0-2) 

`Registry.process` treats a passing HMAC check as proof the whole request (including `request.shop`) is authentic, and forwards `request.shop` unmodified to the app-provided handler: [4](#0-3) 

Because `Context.api_secret_key` is one value shared by every shop that installs the app (there is no per-shop secret in `Context`) [1](#0-0) , any merchant who legitimately installs the app can trigger a real webhook against their own store, capture the resulting `(raw_body, hmac)` pair (a valid signature under the shared secret), and then send it directly to the app's registered callback URL with the `x-shopify-shop-domain` header rewritten to a different, victim shop. The equality that should hold — `shop authenticated by HMAC == shop delivered to the handler` — is broken: the HMAC only certifies `body == HMAC(body, secret)`, never `shop == HMAC-bound-shop`.

The gem's own webhook docs establish that host apps are expected to trust `data.shop` directly as the tenant key, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`, reinforcing that this field is meant to be an authenticated identity, not an untrusted header.

### Impact Explanation
This is a cross-tenant integrity/data-injection issue: an attacker with legitimate access to only their own shop's installation can make the app process arbitrary webhook payloads under a different (victim) shop's identity. Depending on how the host app uses `data.shop` (e.g., looking up the victim's persisted session/access token to react to the "webhook", updating per-shop cached state, etc.), this can lead to cross-tenant state corruption or actions being taken using a session keyed to a shop the attacker doesn't control, satisfying the "Critical - cross-tenant access" bar for this scan.

### Likelihood Explanation
Exploitation requires only that the attacker be permitted to install the app on at least one shop (a completely unprivileged, normal usage flow for any public/multi-tenant Shopify app) and that they can reach the app's webhook HTTP endpoint directly (which is, by design, a public endpoint reachable from the internet, not gated by IP allowlisting for Shopify's servers in this gem). No access to `api_secret_key`, tokens, or victim credentials is required.

### Recommendation
Bind the shop (and ideally topic/webhook id/api version) into the HMAC-authenticated envelope, e.g., by including the relevant Shopify webhook headers in `to_signable_string`, or by independently verifying that the shop header corresponds to an app installation the receiving app expects before trusting it. At minimum, document/require that host applications cross-check `data.shop` against a known, previously-authenticated session/shop record before using it as a tenant key, since the raw header value carries no cryptographic authenticity in this gem today.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` (a normal, unprivileged install).
2. Attacker triggers any subscribed webhook topic on their own store (e.g., updates a product), and captures the raw POST body and the `x-shopify-hmac-sha256` header Shopify sends — this HMAC is valid because it's computed with the app's single, shared `api_secret_key`.
3. Attacker replays that exact `(raw_body, hmac)` pair directly to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC from `raw_body` alone and it matches, so `Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) proceeds and calls the app's handler with `shop: "victim.myshopify.com"`, `topic`, and `body` fully attacker-controlled — despite Shopify never having sent this webhook for `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/context.rb (L8-9)
```ruby
    @api_key = T.let("", String)
    @api_secret_key = T.let("", String)
```

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

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
