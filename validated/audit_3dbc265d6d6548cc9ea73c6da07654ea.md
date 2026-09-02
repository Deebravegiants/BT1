### Title
Webhook `shop` domain is not covered by the HMAC signature, enabling cross-tenant webhook spoofing via replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` verifies the HMAC over the request body alone. The `shop` value (from the `X-Shopify-Shop-Domain` / `shopify-shop-domain` header) is never included in the signed material, yet `Registry.process` reads that unauthenticated header and forwards it as `shop:` in `WebhookMetadata` straight to the app's handler, with the docs explicitly describing it as "The shop domain of the webhook" for the handler to trust and act on.

### Finding Description
The identity binding that should hold is: `shop value verified by HMAC == shop value acted on by the handler`. In this gem that equality is broken.

- `Request#hmac` reads `shopify-hmac-sha256` from headers. [1](#0-0) 
- `Request#to_signable_string` returns only the raw body — no headers, including `shop`, are part of the signed string. [2](#0-1) 
- `Request#shop` is read straight from the (unsigned) `shop-domain` header. [3](#0-2) 
- `HmacValidator.validate` computes and compares the signature only against `to_signable_string` (the body), never against `shop`. [4](#0-3) 
- `Registry.process` validates the HMAC and then constructs `WebhookMetadata` using `request.shop` (the unverified header) as the tenant identifier passed to the app's handler. [5](#0-4) 
- The documentation instructs app authors to treat `data.shop` as "The shop domain of the webhook" and use it directly (e.g. `shop_domain: data.shop`) when enqueuing/processing work, reinforcing that this field is meant to be trusted as the tenant key. [6](#0-5) 

Because the HMAC only binds the body content to the app's secret, and never binds the `shop` header, any request whose body+HMAC pair is valid (for *any* shop) will pass `Registry.process`'s validation check regardless of what `shop` header is attached to that request. An attacker who is a merchant on their own shop (Shop A) — an unprivileged, legitimately installed user of the app, with no access to the app's `client_secret` or any other tenant's credentials — receives genuine webhook deliveries from Shopify for their own store, each with a body and a valid `X-Shopify-Hmac-Sha256` signature. Because the signature never covers `X-Shopify-Shop-Domain`, the attacker can resend the exact same body+HMAC pair to the app's webhook endpoint while substituting `X-Shopify-Shop-Domain: shop-b.myshopify.com` (a different tenant of the same multi-tenant app). `HmacValidator.validate` still returns `true` because the body/HMAC pair is genuinely valid, and `Registry.process` forwards `shop: "shop-b.myshopify.com"` together with Shop A's body content to the handler.

### Impact Explanation
This crosses a tenant boundary: data that was only ever authenticated as belonging to Shop A is delivered to the application labeled as belonging to Shop B, with no cryptographic property tying `shop` to the signed payload. Any host application that follows this gem's documented pattern (`data.shop` as the tenant key to write to a database, trigger jobs, update per-shop state, etc., exactly as shown in the gem's own docs) is exposed to cross-tenant data injection/corruption purely from a low-privileged legitimate app-installer. This matches the "Critical - cross-tenant access" impact category, since one merchant's webhook traffic can be attributed to and processed under a different merchant's identity.

### Likelihood Explanation
High. Exploitation requires no secrets, no privileged access, and no interception — only that the attacker (or any user) is themselves a legitimate installer of the target multi-tenant app, which is the normal, unprivileged position of any merchant. They only need to capture one of their own genuine webhook deliveries (trivial, since they receive them routinely) and resend it with a different `Shop-Domain` header value.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) as part of the HMAC-signed material, or otherwise cryptographically bind the `shop` header to the signed payload before it is trusted. At minimum, `Utils::HmacValidator`/`Webhooks::Request` should not allow `WebhookMetadata#shop` to be treated as verified data; the library should either compute the HMAC over `shop + raw_body` (matching how it already binds `shop` in `Auth::Oauth::AuthQuery#to_signable_string`), or explicitly document that `shop` is unauthenticated and must be independently reconciled against the app's own webhook-registration/session records before being used as a tenant key.

### Proof of Concept
```ruby
# Attacker owns/legitimately controls "shop-a.myshopify.com" and has installed the target app.
# Shopify sends the attacker a genuine webhook for their own store:
raw_body = '{"id": 123, "note": "hello"}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), APP_SECRET, raw_body) # computed by real Shopify

# Attacker replays the SAME body+hmac, but swaps the shop-domain header:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(valid_hmac),   # unchanged, still valid for this body
  "x-shopify-shop-domain" => "shop-b.myshopify.com",        # victim tenant, attacker-chosen
  "x-shopify-webhook-id" => "attacker-chosen-id",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) => true, because it only checks raw_body against the hmac.
# The app's handler receives WebhookMetadata(shop: "shop-b.myshopify.com", body: {...from shop A...})
# and processes/stores Shop A's data under Shop B's identity.
``` [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
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

**File:** docs/usage/webhooks.md (L12-30)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
```
