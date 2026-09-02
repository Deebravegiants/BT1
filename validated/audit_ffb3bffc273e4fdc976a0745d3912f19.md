### Title
Webhook `shop`, `topic`, and `webhook_id` fields are not covered by the HMAC, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so the HMAC signature that `Utils::HmacValidator` verifies covers `@raw_body` alone. [1](#0-0)  Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all read straight out of unauthenticated HTTP headers. [2](#0-1)  `Registry.process` validates the HMAC and then trusts those header-derived fields when building the object handed to the app's handler. [3](#0-2) 

### Finding Description
The binding that should hold is: `shop == tenant the signed body actually belongs to`. Because `HmacValidator.validate` only feeds `verifiable_query.to_signable_string` (the raw body) into the HMAC comparison, [4](#0-3)  the `shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, and `shopify-api-version` headers are never authenticated. `Registry.process` only checks `Utils::HmacValidator.validate(request)` before dispatching to the handler with `request.shop`, `request.topic`, etc: [5](#0-4) 

An unprivileged internet user who can install the app on their own store (a normal, unprivileged action) receives real webhook deliveries with a valid `(body, hmac)` pair signed with the shared `api_secret_key`. Because the HMAC is computed only over the body and does not depend on the shop, the attacker can replay that exact `(body, hmac)` pair to the app's webhook endpoint while forging the `x-shopify-shop-domain` header to name a victim shop. `Registry.process` will accept it as valid (the HMAC over the body still matches) and hand the handler a `WebhookMetadata` claiming the payload came from the victim shop. [6](#0-5) 

This is the exact "field acted on but not covered by the HMAC" identity-binding break called out in scope: `shop` is trusted by the handler but is not part of the signed material.

### Impact Explanation
Any host application that uses `data.shop` from the processed webhook to key its per-tenant storage (the documented and expected usage pattern shown in `docs/usage/webhooks.md`) [7](#0-6)  can be tricked into writing/associating another merchant's data under the wrong tenant, or into triggering tenant-scoped side effects (e.g. uninstall/GDPR handling, order data, customer data) for a shop the attacker does not control. This is a cross-tenant confidentiality/integrity break driven entirely by unauthenticated header data, meeting the "cross-tenant access" Critical impact bar.

### Likelihood Explanation
The prerequisite is only that the attacker be able to install the app on a shop they control (the normal, unprivileged onboarding flow for any Shopify app) in order to obtain one legitimately signed `(body, hmac)` pair, then replay it with a forged `shop-domain` header to the app's public webhook endpoint. No access token, `api_secret_key`, or privileged account is required, making this practically exploitable by any internet user who can install the target app.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the signed material that is verified, or independently cross-check the `shop` header against a value bound to the delivery — e.g., verify the `x-shopify-shop-domain` header matches a shop the app is aware of/expects for the correlated webhook subscription/registration, or extend `to_signable_string` to include the authenticated headers so a forged shop invalidates the HMAC, matching how `Oauth::AuthQuery#to_signable_string` folds `shop` into the signed string. [8](#0-7) 

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger any webhook topic the app subscribes to and capture the raw POST body `B` and the resulting `X-Shopify-Hmac-Sha256` header value `H` (computed as `HMAC-SHA256(api_secret_key, B)`).
2. Send a new POST to the app's webhook endpoint with the exact same body `B` and header `H`, but set `X-Shopify-Shop-Domain: victim.myshopify.com` (and optionally forge `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
3. `ShopifyAPI::Webhooks::Registry.process` computes `HmacValidator.validate(request)` over `request.to_signable_string` (= `B`) and finds it matches `H`, so validation passes. [9](#0-8) 
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and the attacker-authored body `B`, even though `victim.myshopify.com` never sent this request. [6](#0-5)

### Citations

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
