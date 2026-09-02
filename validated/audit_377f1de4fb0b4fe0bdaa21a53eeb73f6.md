### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `HmacValidator.validate` verifies the HMAC solely over that body [1](#0-0) . The `shop` value, taken from the `shopify-shop-domain`/`x-shopify-shop-domain` header, is never included in the signed content [2](#0-1) , yet `Registry.process` passes this unauthenticated value straight to the app's handler as the tenant identifier (`WebhookMetadata#shop`) once HMAC validation over the body passes [3](#0-2) [4](#0-3) .

### Finding Description
The identity binding that should hold is: `hmac == HMAC(secret, shop || body)`, i.e. the shop the app trusts for a webhook must be cryptographically bound to the same bytes that were verified. Instead the actual binding implemented is `hmac == HMAC(secret, body)` while `shop` is read out-of-band from a header that carries no signature coverage:

- `Request#to_signable_string` only returns `@raw_body` [1](#0-0) .
- `Request#shop` reads the `shopify-shop-domain` header directly, with no cryptographic tie to the HMAC [2](#0-1) .
- `HmacValidator.validate`/`validate_signature` compute and compare the signature purely against `verifiable_query.to_signable_string` (the body) [5](#0-4) .
- `Registry.process` gates the entire operation on this body-only HMAC check, then forwards `request.shop` (unverified) into `WebhookMetadata`, which the host app's handler will use as the tenant/shop key for state changes such as data redaction, order updates, or app-uninstall bookkeeping [3](#0-2) .

Because the `api_secret_key` is shared across every shop that has installed the app, any merchant who has installed the app (an ordinary, unprivileged installation - not a leaked credential or privileged account) legitimately receives real webhook deliveries containing a valid `(body, hmac)` pair for their own store. Since the HMAC never covers the shop header, that exact `(body, hmac)` pair remains valid when replayed with an arbitrary `shopify-shop-domain` header value pointing at a different (victim) shop. `Registry.process` will accept it and hand the handler a `WebhookMetadata` claiming to be for the victim shop, even though nothing in the verified bytes ties the payload to that shop.

### Impact Explanation
This breaks the tenant-binding guarantee the gem is supposed to provide to host applications: "if `Utils::HmacValidator.validate` succeeds, the delivery genuinely originates for `request.shop`." Host apps that rely on this gem's webhook processing to authenticate the shop associated with a webhook (a documented, intended use of `Registry.process`/`WebhookMetadata#shop`) can be tricked into applying data intended for one merchant to another merchant's tenant record - i.e., cross-tenant access/injection using only a validly-issued webhook from the attacker's own shop. This satisfies the Critical impact bar of cross-tenant access without requiring the app's `client_secret`, an access token, or any privileged credential.

### Likelihood Explanation
Exploitability only requires:
1. Installing the target app as an ordinary merchant (not privileged, no leaked secrets needed).
2. Capturing one legitimately delivered webhook body + HMAC for a chosen topic (many webhook bodies contain attacker-controlled or predictable content, e.g. `app/uninstalled`, `shop/update`, or bodies the attacker fully controls via their own shop's data).
3. Replaying the exact body/HMAC with the `shopify-shop-domain` header rewritten to the victim's domain.

No cryptographic secret needs to be broken; only the header value needs to be changed, which the gem does not authenticate at all.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the bytes that are HMAC-verified, or otherwise cryptographically bind the header-derived `shop` to the verified payload before it is trusted by `Registry.process`/`WebhookMetadata`. At minimum, document/enforce that `shop-domain` is untrusted metadata and require host apps to independently verify the shop is one that is actually installed and expected, rather than presenting it as a verified field of `WebhookMetadata`.

### Proof of Concept
```ruby
# Attacker installs the app on their own shop "attacker.myshopify.com"
# and receives a legitimate webhook delivery for topic "app/uninstalled":
raw_body = '{"some":"content controlled or predictable by attacker"}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), api_secret_key, raw_body)

# Attacker replays it, claiming to be "victim-shop.myshopify.com":
forged_headers = {
  "x-shopify-topic" => "app/uninstalled",
  "x-shopify-hmac-sha256" => Base64.encode64(valid_hmac), # still valid! body unchanged
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # not covered by HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate passes (body-only check), handler receives
#    WebhookMetadata(shop: "victim-shop.myshopify.com", ...) despite the
#    webhook never actually originating for that shop.
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
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
