### Title
Webhook shop attribution is not covered by HMAC verification, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so the HMAC signature validated by `ShopifyAPI::Utils::HmacValidator` never covers the `x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`, or `x-shopify-api-version` headers. `ShopifyAPI::Webhooks::Registry.process` nonetheless trusts `request.shop` (and `request.topic`) verbatim once the body HMAC passes, and hands them to the app's `WebhookHandler` as the authoritative tenant identity for the event. This breaks the identity binding: `shop used to attribute webhook effects == shop authenticated by HMAC` does not hold, because the HMAC only authenticates the body bytes, not the shop.

### Finding Description
`lib/shopify_api/webhooks/request.rb`:
```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from headers with no cryptographic binding to the body: [2](#0-1) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the expected signature purely from `verifiable_query.to_signable_string`, i.e. the raw body, and compares it to the `hmac-sha256` header: [3](#0-2) 

`ShopifyAPI::Webhooks::Registry.process` validates only that HMAC, then dispatches to the registered handler using the unauthenticated `request.shop` and `request.topic`:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [4](#0-3) 

The documented integration pattern in `docs/usage/webhooks.md` explicitly tells developers that `Registry.process` "will verify the request did indeed come from Shopify," and shows `data.shop` being used directly as the tenant identifier without any additional shop verification step: [5](#0-4) 

Because Shopify apps use a single `api_secret_key` shared across all installed shops (this is also visible in the test fixtures, where the same secret signs webhooks for any `shop.myshopify.com`), any unprivileged user who installs the app on their own store can obtain a validly-signed `(body, hmac)` pair for their own shop, then replay that exact body/hmac pair to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (and optionally `x-shopify-topic`) header. `HmacValidator.validate` still succeeds because it only checks the body bytes, and `Registry.process` attributes the (unmodified) body to the attacker-chosen shop.

### Impact Explanation
This is a cross-tenant identity-binding break at Critical severity: an attacker who legitimately installs the app on their own store (no privileged access, no credential leakage, no TLS interception required) can cause the app to process webhook payloads under an arbitrary victim shop domain of their choosing. Any app logic that keys persistence, authorization, or compliance actions (e.g. `customers/redact`, `orders/create`) off `WebhookMetadata#shop`—exactly as shown in the gem's own documentation example—will attribute attacker-controlled data to a shop the attacker does not control, corrupting or injecting data cross-tenant.

### Likelihood Explanation
High likelihood for any app following the documented `Registry.process` pattern verbatim (as shown in `docs/usage/webhooks.md`) without an out-of-band check that the reported shop is a currently-installed/known shop. The only prerequisite is a free/self-service app installation by the attacker to obtain one valid `(body, hmac)` pair from their own webhook traffic, which is then replayed with a modified `shop-domain` header — no secret key, access token, or network interception of another party's traffic is needed.

### Recommendation
Include the shop domain (and ideally topic, webhook_id, api_version) in the HMAC-signed payload, or otherwise independently verify that `request.shop` corresponds to a shop for which the app currently holds a valid, previously-established session/installation before dispatching the webhook to a handler. At minimum, document that `Registry.process` does not authenticate the shop-domain header and that consuming apps must validate `data.shop` against their own known-installed-shops store before trusting it.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` (self-service, no special privilege).
2. Attacker triggers a real event (e.g. creates an order) causing Shopify to POST a genuinely-signed webhook to the app's public webhook endpoint:
   - `x-shopify-topic: orders/create`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-hmac-sha256: <valid HMAC over raw body>`
3. Attacker captures this request from their own inbound traffic (their own server/logs — not another party's traffic).
4. Attacker replays the identical `raw_body` and `x-shopify-hmac-sha256` value to the same public webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which only checks the raw body against the HMAC — this passes.
6. The `orders/create` handler executes with `data.shop == "victim-shop.myshopify.com"`, even though the payload actually originated from, and was only ever signed for, `attacker-shop.myshopify.com`.

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
