### Title
Webhook shop/topic identity fields are not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , while the `shop`, `topic`, `api_version`, and `webhook_id` fields are read straight from HTTP headers that are never part of the signed bytes [2](#0-1) . `Registry.process` validates only the body's HMAC and then dispatches on the unsigned `topic`/`shop` values, handing them to the app's handler as trusted tenant identity [3](#0-2) .

### Finding Description
The equality this breaks is: *bytes verified* (only `@raw_body`, per `to_signable_string`) *≠ bytes acted on* (`shop`, `topic`, `webhook_id`, `api_version`, all taken from `@headers` and never mixed into the HMAC computation) [4](#0-3) .

`Utils::HmacValidator.validate` recomputes the signature purely from `verifiable_query.to_signable_string` and compares it with `verifiable_query.hmac` [5](#0-4) . For a `Webhooks::Request`, that signable string is the raw body only. `Registry.process` treats a passing HMAC check as proof of the whole request's authenticity and then uses `request.topic` to select the registered handler and `request.shop` as the tenant identity handed to the app via `WebhookMetadata` [3](#0-2) :

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
end
```

Because `shop`/`topic` are outside the signed payload, any attacker who can obtain one validly-signed webhook body/HMAC pair for *any* shop (e.g., by triggering a webhook to an endpoint they control for their own store, or intercepting one) can resend that exact body+HMAC to the target app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` and/or `X-Shopify-Topic` headers with values naming a different, victim shop. `HmacValidator.validate` still succeeds because only the body bytes are checked, and `Registry.process` will happily route this forged request to the handler for the attacker-chosen topic, tagging it with the attacker-chosen `shop`.

### Impact Explanation
This is a cross-tenant identity confusion vulnerability: the app's webhook handler receives a `WebhookMetadata` claiming to be from shop B while the payload content and topic are actually attacker-controlled data from shop A. Typical webhook handlers use `shop` to look up that shop's stored session/access token and perform mutations scoped to it, or to react to mandatory lifecycle topics (`app/uninstalled`, `shop/redact`, `customers/redact`, `customers/data_request`) which this library explicitly special-cases as `MANDATORY_TOPICS` [6](#0-5) . An attacker can therefore forge a passing-HMAC webhook naming an arbitrary victim shop and an arbitrary topic (as long as the body shape matches what their own handler code expects to parse), causing the app to execute shop-scoped side effects — including data redaction/uninstall workflows or writes performed using the victim's stored access token — for a shop the attacker does not control. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
The attacker needs no secret material: they only need a legitimate signed webhook body (obtainable from their own store, since any merchant/developer can install and receive webhooks for it) and the ability to POST to the target app's public webhook endpoint with arbitrary headers, which is normal unauthenticated internet access. The documented usage pattern in this gem forwards raw headers directly into `Webhooks::Request` without any additional binding [7](#0-6) , so any app following the documented integration is exposed.

### Recommendation
Bind the tenant-identifying fields into the signed payload verification, or otherwise cross-check them against a value the app already trusts (e.g., verify `request.shop` against the shop associated with the currently loaded/active session before processing, and consider incorporating `shop`/`topic` into an application-level HMAC context) rather than trusting header values whose only "proof" is an HMAC computed over unrelated body bytes.

### Proof of Concept
1. Attacker installs/owns "attacker-shop.myshopify.com" and registers a webhook (e.g. `orders/create`) pointing to the target app's endpoint, so Shopify legitimately delivers a webhook with a valid `X-Shopify-Hmac-Sha256` computed over the raw body using the app's real secret.
2. Attacker captures the raw body + HMAC header of that delivery.
3. Attacker replays the exact same raw body and HMAC header to the same app endpoint, but changes `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com` (and/or `X-Shopify-Topic` to `app/uninstalled` if the body shape is compatible with that handler's expectations).
4. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the signature from the (unchanged) raw body and it matches, so `Registry.process` proceeds and invokes the handler with `shop: "victim-shop.myshopify.com"`, even though nothing about this request actually originated from or was authorized by that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L8-12)
```ruby
      MANDATORY_TOPICS = T.let([
        "shop/redact",
        "customers/redact",
        "customers/data_request",
      ].freeze, T::Array[String])
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

**File:** docs/usage/webhooks.md (L125-136)
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
```
