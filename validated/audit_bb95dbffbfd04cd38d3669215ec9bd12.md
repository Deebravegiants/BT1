### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` fields are trusted after HMAC verification but are not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking that `hmac` matches an HMAC computed over the raw request body [1](#0-0) . However, the `shop`, `topic`, `webhook_id`, and `api_version` values that are handed to the app's handler as trusted, verified identity data come straight from unauthenticated HTTP headers and are never included in the signed payload.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [2](#0-1) , while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, `shopify-api-version`) with no cryptographic binding to the HMAC [3](#0-2) .

`HmacValidator.validate` computes the signature only from `verifiable_query.to_signable_string` (i.e., the raw body) and compares it against the `hmac` header [4](#0-3) . After this check passes, `Registry.process` builds `WebhookMetadata` directly from `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` and hands it to the app's handler as verified data [5](#0-4) . The documentation explicitly tells integrators to trust `data.shop` as "The shop domain of the webhook" after `process` succeeds [6](#0-5) [7](#0-6) .

Because HMAC is computed with the app's single shared `api_secret_key` across *all* shops that install the app (not per-shop), an attacker who controls their own shop installation of the app can legitimately trigger Shopify to send a webhook to the app with a validly-signed body. Since the signature covers only the body bytes and not the `shop` header, the attacker can replay that exact body+HMAC pair to the app's webhook endpoint while substituting an arbitrary victim `shop` domain in the `x-shopify-shop-domain` header. `HmacValidator.validate` will still pass (it only checks the body against the shared secret), and the handler will receive `WebhookMetadata` claiming the payload originated from the victim shop.

This breaks the identity binding: **shop claimed in `WebhookMetadata.shop` == shop that actually produced/authorized the payload**. The gem verifies "bytes" (raw body) but the host application's business logic keys off `shop`, a field the gem does not verify.

### Impact Explanation
This is a cross-tenant identity-confusion primitive baked into the gem's own webhook verification API: the field applications are documented to rely on for shop/tenant identification (`data.shop`) is not covered by the cryptographic check the gem performs (`Utils::HmacValidator.validate`). Any application built exactly as documented (mapping webhook body content by `data.shop`) inherits a cross-tenant data/action confusion vulnerability, without any misuse of the gem's API.

### Likelihood Explanation
Exploitation requires the attacker to control at least one legitimate installation of the target app (a trivial, unprivileged step for any public app — the attacker installs the app on their own free development store), which is enough to obtain a validly-HMAC-signed payload under the shared `api_secret_key`. Replaying that payload with a forged `shop` header against the app's public webhook endpoint is straightforward, since no other binding exists.

### Recommendation
Include the identity-critical headers (`shop`, `topic`, `webhook_id`, `api_version`) in the string that is HMAC-verified, or otherwise cryptographically bind them to the signed payload, rather than exposing them as separately-trusted, unauthenticated fields in `WebhookMetadata`. At minimum, document prominently that `data.shop`/`data.topic`/etc. are NOT covered by the HMAC check and must not be used for authorization or tenant-scoping decisions without additional verification (e.g., cross-checking against a shop that is known to have this webhook_id registered).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`, obtaining valid webhook deliveries signed with the app's `api_secret_key`.
2. Attacker triggers/receives a webhook (e.g., `orders/create`) whose body they can craft/control on their own store, and captures the resulting `x-shopify-hmac-sha256` header value, which is `HMAC-SHA256(api_secret_key, raw_body)` per `HmacValidator#compute_signature` [8](#0-7) .
3. Attacker sends a new POST to the app's registered webhook endpoint with the identical `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers [9](#0-8) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the secret [1](#0-0) .
5. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the application to process attacker-controlled webhook content as if it were authoritatively sent for the victim shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L33-40)
```ruby
        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
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

**File:** docs/usage/webhooks.md (L124-135)
```markdown

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
