### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross‑tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by recomputing an HMAC over the raw request body, but the `shop` value that is handed to the webhook handler (and used by the host app to attribute the payload to a tenant) is read straight from an HTTP header that the HMAC never covers. Any party who can obtain one genuine `(body, hmac)` pair for the shared app secret can replay it with a different `shop-domain` header and have it accepted as if it came from a different merchant.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Webhooks::Request#shop` is populated directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no cryptographic tie to the body or the HMAC: [2](#0-1) 

`Utils::HmacValidator` verifies the HMAC purely against `to_signable_string` (i.e. the body) and the app's `api_secret_key`: [3](#0-2) 

`Registry.process` checks only this body-HMAC, then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler — the equality it should be enforcing (`hmac ⇒ this body came from *this* shop`) is never checked; only `hmac ⇒ this body came from *some* holder of api_secret_key` is checked: [4](#0-3) 

Because `api_secret_key` is a single **per-app** secret shared across every merchant that installs the app (it is not per-shop), any merchant who has installed the app can:
1. Trigger a real webhook delivery to their own shop for a topic they control the content of (e.g. `orders/create`), capturing the genuine `X-Shopify-Hmac-SHA256` value Shopify computed over that body.
2. Replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint, but substitute the `X-Shopify-Shop-Domain` header with a victim shop's domain.
3. `HmacValidator.validate` still succeeds (it only checks body+secret), so `Registry.process` dispatches the handler with `WebhookMetadata#shop` set to the victim's domain, even though the payload never originated from that shop.

This is the same class of bug as the reference report: a cryptographic guard (HMAC / liquidation-grace-timer) protects one field, while a different, unprotected field is what the calling code actually trusts and acts on (`shop` vs. signed body; unhealthy-position vs. cleared-warning flag).

### Impact Explanation
This breaks the binding "`shop` used to route/attribute webhook data == shop that actually produced the signed payload." Any application built on this gem that keys tenant-scoped side effects (e.g., updating the correct shop's DB row, revoking data, crediting orders, syncing inventory) off `WebhookMetadata#shop` without independently re-verifying it against its own list of installed shop domains is exposed to cross-tenant data confusion/injection — data or actions intended for the attacker's own shop can be attributed to an arbitrary victim shop known to be using the app. This matches the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is realistic but requires: (a) the attacker to be a legitimate (if unprivileged/uninstall-scale) user of the target app on some shop, and (b) the host application to trust `WebhookMetadata#shop` as the tenant key without additional verification (a common pattern, since the gem's own docs/tests treat `data.shop` as authoritative). No secrets, TLS interception, or privileged access are required — only normal use of a legitimately-installed instance of the app plus replaying an HTTP request with a modified header.

### Recommendation
Bind the verified shop identity to the HMAC-protected payload rather than trusting the header alone: include the shop domain (or the webhook resource's own body-embedded shop identifier) in the value that is HMAC-verified, or require the host application to cross-check `request.shop` against a known/installed-shops list before processing, and document this requirement prominently since the gem currently exposes `request.shop` as if it were authenticated.

### Proof of Concept
```ruby
# Attacker installs the app on their own shop "attacker.myshopify.com" and
# receives a genuine webhook for a topic whose body they control the content of.
# They capture the real headers Shopify sent them, e.g.:
raw_body = '{"id": 1, "note": "malicious payload chosen by attacker"}'
real_hmac_header = "..."  # copied verbatim from Shopify's genuine request to attacker's shop

# Attacker now replays the exact same body+hmac to the app's webhook endpoint,
# but swaps only the shop-domain header:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => real_hmac_header,   # still valid! HMAC only covers raw_body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",  # spoofed
  "x-shopify-webhook-id" => "attacker-controlled-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# This succeeds because HmacValidator only checks raw_body against api_secret_key:
ShopifyAPI::Webhooks::Registry.process(request)
# => handler receives WebhookMetadata with shop == "victim-shop.myshopify.com"
#    even though the payload never came from that shop.
```
Relevant code paths exercised: [4](#0-3)  and [5](#0-4) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
