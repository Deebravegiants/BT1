### Title
Webhook `shop` field is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` reads the `shop` (and `topic`, `webhook_id`, `api_version`) values directly from HTTP headers, while `to_signable_string` — the data actually covered by the HMAC signature check in `ShopifyAPI::Utils::HmacValidator.validate` — only returns the raw request body. This is exactly the bug class from the report: a field that is acted upon (`shop`) is not bound by the cryptographic check (`hmac`) that is supposed to authenticate the whole request.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers that are never part of the signed material: [2](#0-1) 

`ShopifyAPI::Webhooks::Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which internally recomputes the HMAC over `to_signable_string` (the body only) and compares it to the `hmac` header: [3](#0-2) [4](#0-3) 

Once the signature check passes, `request.shop` (an unauthenticated header value) is forwarded verbatim into `WebhookMetadata` and handed to the host app's handler as the tenant identifier: [5](#0-4) 

The gem's own documentation tells integrators that `Registry.process` "will verify the request did indeed come from Shopify" and that `data.shop` is "The shop domain of the webhook": [6](#0-5) [7](#0-6) 

but the binding `hmac(body) == HMAC_secret(body) ⇒ shop == originating shop` does not hold, because `shop` is never part of the signed bytes. Any request bearing a *valid* `(raw_body, hmac)` pair — trivially obtainable by any unprivileged party who can install the app on their own store and capture one legitimately delivered webhook for that store — will pass validation for **any** `shop-domain` header value the attacker chooses to send along with it.

### Impact Explanation
This breaks a tenant-identity binding: `bytes verified (raw_body) != bytes acted on (shop header)`. An attacker who legitimately installs the target app on their own store (no special privileges, no `api_secret_key`, no access token) can capture one real Shopify-delivered webhook `(raw_body, hmac)` and replay it to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header. `HmacValidator.validate` still returns `true` because it only checks the body against the HMAC. The host app's handler then processes the (attacker-controlled/replayed) body as if it originated from the victim shop identified in the spoofed header, resulting in cross-tenant data processing/corruption under the wrong tenant's identity. This matches the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Any developer with legitimate access to a public/development app install (an unprivileged internet user in the sense that no secret material or elevated account is required) can trivially capture one valid webhook body+HMAC and replay it with a forged shop header against the same app's public webhook endpoint. No credentials, TLS interception, or social engineering are required — only observation of traffic the attacker is already authorized to receive for their own store.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) values into the material that is authenticated, or otherwise cryptographically verify that the `shop-domain` header matches the tenant the caller is authorized to act as before trusting it in `WebhookMetadata`. At minimum, document/require that host apps cross-check `data.shop` against records of shops that have actually registered the corresponding `webhook_id`/topic, rather than treating a passing HMAC check as proof that the `shop` header is trustworthy. Concretely, `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb` line 190) should not implicitly vouch for `request.shop`'s authenticity via the body-only HMAC check.

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled development store `attacker-shop.myshopify.com`.
2. Trigger any webhook topic the app is subscribed to (e.g. `orders/create`) and capture the raw POST: `raw_body` and the `X-Shopify-Hmac-Sha256` header — this pair is validly signed by Shopify with the app's shared secret.
3. Replay the exact same `raw_body` and `hmac` header to the app's public webhook endpoint, but replace the `X-Shopify-Shop-Domain` header with `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against `hmac`; `request.shop` is never validated.
5. The host app's handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and processes attacker-supplied `raw_body` content under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
```ruby
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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L123-136)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```
```
