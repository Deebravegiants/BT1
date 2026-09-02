I have sufficient evidence to produce the analog finding.

### Title
Webhook `shop` identity is not covered by the HMAC, enabling cross-tenant webhook shop-spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` verifies the HMAC over the raw request body only, while the `shop` field that identifies which tenant the webhook belongs to is taken from an HTTP header that is never included in the signed bytes. Any party who can obtain one validly-signed webhook delivery (e.g., by installing the app on their own store, since webhook HMACs are computed with the single app-wide `client_secret` shared across every shop that installs the app) can replay that same body/HMAC pair while substituting the `X-Shopify-Shop-Domain` header for any victim shop. `Registry.process` accepts this forged identity and hands it to the host application's handler as trusted data.

### Finding Description
`HmacValidator.validate` computes the signature exclusively over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw body: [2](#0-1) 

But `shop` (the tenant identity) is read straight from an unauthenticated header, entirely outside the signed data: [3](#0-2) 

`Registry.process` validates only the body HMAC and then forwards `request.shop` — the unsigned header value — into `WebhookMetadata`, which is passed to the app's handler as the authoritative tenant identifier: [4](#0-3) [5](#0-4) 

The broken binding, stated as an equality that should hold but does not:
`shop_that_signed(raw_body, hmac) == request.shop` — this is never checked; only `hmac == HMAC(secret, raw_body)` is checked, independent of `shop`.

Because Shopify webhook HMACs are generated with a single per-app `client_secret` shared across **every** shop that installs the app (not a per-shop secret), an attacker who installs the app on a shop they control receives real, validly-signed webhook deliveries for that shop. They can then re-POST the identical `(raw_body, hmac)` pair to the app's webhook endpoint while swapping only the `X-Shopify-Shop-Domain`/`Shopify-Shop-Domain` header to a victim shop's domain. `Utils::HmacValidator.validate` still returns `true` because it never inspects the header, and `Registry.process` dispatches the handler with `WebhookMetadata.new(shop: <victim-shop>, ...)`.

### Impact Explanation
This crosses a tenant boundary using only the attacker's own (legitimately obtained) webhook credentialing, without needing the app's `client_secret`, an access token, or any privileged account — the attacker only needs to install the app on a shop they control, which is the normal unprivileged flow for any Shopify merchant. Host applications that key persisted data, access-token lookups, or business logic off `WebhookMetadata#shop` (as the gem's own documentation instructs them to do) will process/attribute attacker-supplied body content as if it originated from the victim shop, i.e. cross-tenant data confusion/injection. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
High. No secret material is required beyond the ability to install the app once on an attacker-controlled shop (a normal, low-privilege action for any Shopify merchant/app installer), and forging the header requires nothing more than issuing a raw HTTP POST with the header changed — the gem performs no shop-binding check at all.

### Recommendation
Include the shop-identifying header (and ideally topic/webhook-id) inside the signable bytes bound to the HMAC, or independently verify that the shop in the header corresponds to a shop known to have installed the app with a token whose provenance can be checked, before trusting `request.shop`. At minimum, mirror the OAuth/JWT approach used elsewhere in the gem (e.g., binding the `aud`/`dest` claim in `JwtPayload`, see [6](#0-5) ) by making the tenant identity part of the verified payload rather than an out-of-band, unauthenticated header.

### Proof of Concept
```ruby
require "shopify_api"

ShopifyAPI::Context.setup(
  api_key: "key",
  api_secret_key: "shared_app_secret",
  # ...
)

# Attacker installs the app on their own shop "attacker.myshopify.com"
# and receives a real webhook delivery signed with the shared app secret:
raw_body = '{"id":1,"note":"legit order on attacker shop"}'
hmac = Base64.strict_encode64(
  OpenSSL::HMAC.digest("sha256", "shared_app_secret", raw_body)
)

# Attacker replays identical body+hmac but swaps only the shop header:
forged_headers = {
  "shopify-topic" => "orders/create",
  "shopify-hmac-sha256" => hmac,
  "shopify-shop-domain" => "victim-shop.myshopify.com", # not covered by hmac
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# Passes because HmacValidator only checks raw_body:
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

# Registry.process will now dispatch to the handler with shop: "victim-shop.myshopify.com"
ShopifyAPI::Webhooks::Registry.process(request)
```

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-23)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end

    module WebhookHandler
      include Kernel
      extend T::Sig
      extend T::Helpers
      interface!

      sig do
        abstract.params(data: WebhookMetadata).void
      end
      def handle(data:); end
```

**File:** lib/shopify_api/auth/jwt_payload.rb (L43-45)
```ruby
        raise ShopifyAPI::Errors::InvalidJwtTokenError,
          "Session token had invalid API key" unless @aud == Context.api_key
      end
```
