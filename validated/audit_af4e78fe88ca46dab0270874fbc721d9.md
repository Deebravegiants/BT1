### Title
Webhook HMAC signature does not cover `shop-domain`, `topic`, or `webhook-id` headers, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a request as authentically coming from Shopify — and attributable to the `shop` header value — as long as `Utils::HmacValidator.validate(request)` passes. However, the HMAC signature that is validated is computed **only over the raw request body**, never over the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers that the handler actually consumes to decide which tenant/topic the event belongs to.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns just `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes/compares the HMAC solely against that signable string: [2](#0-1) 

`Registry.process` gates on this HMAC check, then unconditionally trusts `request.shop`, `request.topic`, and `request.webhook_id` — all parsed straight from attacker-controllable HTTP headers — to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) [4](#0-3) 

This breaks the intended binding `HMAC(body) == HMAC(body, shop, topic, webhook_id)`: the signature only proves the body bytes are unmodified, not that the accompanying `shop`, `topic`, or `webhook_id` headers were the ones Shopify actually sent alongside that body. The library's own documentation states that `Registry.process` "will verify the request did indeed come from Shopify" and describes `shop` as trustworthy metadata for the handler to act on: [5](#0-4) 

Because the HMAC secret (`api_secret_key`/`client_secret`) is shared across **all shops that install the app** (it is not shop-specific), any installed merchant legitimately receives real webhook deliveries — valid body + valid HMAC — for their own shop. Since the signature never binds to the header values, that merchant can replay the exact same `(raw_body, hmac)` pair to the app's webhook endpoint while substituting a different `shop-domain` header (and/or `topic`/`webhook-id`). `HmacValidator.validate` still succeeds because it only re-derives the HMAC from the untouched body, and the handler is invoked believing the event originates from the spoofed shop.

### Impact Explanation
This is a cross-tenant identity-binding bypass: the tenant identity (`shop`) that the app's handler uses to route data, enqueue jobs, or write to per-shop storage is not the tenant that the cryptographic proof actually covers. A malicious merchant can inject webhook payloads that host apps will attribute to a victim shop, corrupting per-tenant state, or can relabel `topic`/`webhook_id` to trigger unintended handler logic/duplicate-detection bypass under attacker control. This matches the "Critical - cross-tenant access" category, since it lets one tenant impersonate another to the app's webhook processing pipeline using only material Shopify itself sent them for their own store.

### Likelihood Explanation
Likelihood is high for any app that relies on this gem's `Webhooks::Registry.process`/`Webhooks::Request` as documented, since the exploit needs no secrets beyond a normal app installation (any shop that installs the app receives valid signed webhooks and can capture/replay them with modified headers to the app's own callback endpoint). No access to `api_secret_key`, tokens, or the Shopify platform's internals is required — only observing your own shop's webhook deliveries.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable content used by `HmacValidator`, or otherwise cryptographically bind them to the signed body (e.g., construct the signable string from a canonicalized concatenation of headers + body) so that `Utils::HmacValidator.validate` fails if any of these fields are altered relative to what Shopify actually signed. At minimum, document prominently that `Registry.process` verification does not protect header integrity, and require hosting apps to independently corroborate `shop` against a known session/tenant before trusting it.

### Proof of Concept
1. App installs on `shop-a.myshopify.com`; Shopify sends a legitimate webhook to the app's callback URL:
   - headers: `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, `x-shopify-shop-domain: shop-a.myshopify.com`
   - body: `{"id": 123, ...}`
2. The operator of `shop-a` (a normal, unprivileged app user) intercepts/observes this callback (e.g., via their own reverse proxy/logging, or simply by controlling the endpoint that receives it if they run a middleman).
3. They resend the identical `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but change `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers as usual; `Utils::HmacValidator.validate` recomputes HMAC over `@raw_body` only and it matches, so `Registry.process` proceeds and invokes the handler with `shop: "victim-shop.myshopify.com"`, `topic`, and `webhook_id` all attacker-supplied, even though Shopify never sent this event for `victim-shop`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L16-33)
```ruby
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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
