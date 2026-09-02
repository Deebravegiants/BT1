Confirmed. This finding is real and directly matches the requested bug class: "a field acted on but not covered by the HMAC."### Title
Webhook `shop-domain` header is trusted for tenant routing but is not covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by verifying `Utils::HmacValidator.validate(request)`, then immediately hands the app's handler a `WebhookMetadata` object whose `shop` field is taken from `request.shop`. However, `Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `Request#shop` reads the `shop-domain` HTTP header, which is not part of the signed bytes at all [2](#0-1) . The HMAC check only proves the body was signed with the app's shared secret; it proves nothing about which shop the header claims to be.

### Finding Description
`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to the value returned by `verifiable_query.hmac` [3](#0-2) . For `Webhooks::Request`, `to_signable_string` is defined as just `@raw_body` [1](#0-0) , so the `shop-domain` header is never part of what is verified.

`Registry.process` uses this same validated request to build the trust boundary that is handed to the app's business logic:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
  body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
``` [4](#0-3) 

The binding that should hold is: `shop_claimed_in_header == shop_that_produced_the_signed_body`. That binding is never checked — the gem authenticates *bytes* (the raw body against the app's single shared secret, which is identical for every shop the app serves) but then acts on a *field* (`shop-domain`) that isn't cryptographically tied to that body at all. The documented consumption pattern confirms `shop` is meant to identify the tenant for downstream handling/enqueueing: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` [5](#0-4) .

Because the HMAC secret (`Context.api_secret_key`) is the same for all shops installed on a given app, anyone who can obtain one validly-signed webhook body/HMAC pair for *any* shop (e.g., their own store, where they control triggering events and can capture the outbound webhook) can replay that exact `raw_body`/`hmac-sha256` pair to the app's webhook endpoint while substituting an arbitrary victim `shop-domain` header value. `HmacValidator.validate` still passes (it only checks the body bytes against the secret), and `Registry.process` will call the app's handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop domain, alongside the attacker-fabricated `body`.

### Impact Explanation
This breaks the tenant/shop identity binding that every downstream consumer of this gem relies on (`WebhookMetadata#shop` is the only tenant-identifying field surfaced from the verified request). An app that uses `data.shop` to key its per-tenant records, enqueue per-tenant jobs, or update state (exactly as documented) can be made to attribute attacker-controlled webhook content to a shop the attacker does not own — a cross-tenant data-integrity/confidentiality violation reachable by any unprivileged internet user in control of one shop on the same app, without needing the app's `client_secret` or any privileged credential.

### Likelihood Explanation
Reaching this requires only: (1) install/have a shop connected to the target app in a way that lets the attacker trigger a genuine webhook delivery for their own shop (a normal, unprivileged action any merchant can take), (2) capture that request's raw body + `hmac-sha256` header (visible to the receiving endpoint's operator, or interceptable if the attacker controls the store/network path to a proxy they operate), and (3) resend it to the app's public webhook endpoint with a different `shop-domain` header. No secret material, session, or elevated privilege is required — only the ability to control the header on a replayed HTTP request, which the gem never checks.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the value that is cryptographically bound, or otherwise verify the `shop-domain` header against an independent, trusted source (e.g., look up the shop from a locally-stored webhook subscription id rather than trusting the header) before passing it to `WebhookHandler#handle`. At minimum, document prominently that `data.shop` is unauthenticated header data and must not be used as a tenant key without independent verification, and provide a validated alternative.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" and receives a legitimate webhook for it,
# capturing its raw body + valid X-Shopify-Hmac-Sha256 header (signed with the app's
# single shared secret, which is common across all shops on this app).
raw_body = captured_raw_body            # e.g. '{"id":123,"note":"legit order"}'
valid_hmac_b64 = captured_hmac_header    # valid Base64 HMAC-SHA256 over raw_body

# Attacker replays it to the app's webhook endpoint, but swaps the shop header
# to a victim shop that the attacker does not control:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac_b64,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # not covered by the HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# HmacValidator.validate(request) still returns true, because it only checks
# `raw_body` against the shared secret -- it never inspects the shop header.
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...))
# The app's handler now attributes attacker-controlled body content to "victim-shop.myshopify.com".
```

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
