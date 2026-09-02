### Title
Webhook `shop` identity is trusted from an unauthenticated header, not bound by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identifier (`shop`) passed to the app's `WebhookHandler` from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, but the HMAC signature validated by `ShopifyAPI::Utils::HmacValidator` only covers the raw request body. This breaks the binding: `shop header == tenant identity used by handler` is never checked against `shop covered by HMAC`. An attacker who legitimately installs the app on their own store (an unprivileged action available to anyone) can capture a validly-signed webhook delivery for their own shop and replay the identical body/HMAC to the app's webhook endpoint while substituting the `shop-domain` header for a victim shop, causing the app to process/attribute the payload to a different tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from a header with no cryptographic binding: [2](#0-1) [3](#0-2) 

`HmacValidator.validate` computes and compares the HMAC over `verifiable_query.to_signable_string`, i.e. only the body — never the headers: [4](#0-3) 

`Registry.process` accepts the request as authentic once the body HMAC checks out, then forwards the header-derived `shop` value straight into `WebhookMetadata`, which is handed to the app's handler as the trusted tenant identifier: [5](#0-4) [6](#0-5) 

The identity equality that should hold is: `shop bound by HMAC == shop used to key handler.handle`. Because `to_signable_string` only signs `@raw_body`, this equality never holds — `shop` is fully attacker-controllable independent of the signature. The documented pattern explicitly instructs apps to treat the header-derived `shop` in `WebhookMetadata` as trustworthy tenant context (`ShopifyAPI::Webhooks::Registry.process` is presented as the sole authenticity check before dispatching to the handler): [7](#0-6) 

### Impact Explanation
Any user who installs the app on a store they control (no stolen credentials, no privileged access, no knowledge of `api_secret_key` required) receives a validly HMAC-signed webhook for their own shop. Since the signature only binds the body, they can resend the exact same body/HMAC pair to the app's webhook endpoint with an arbitrary `shop-domain` header value. The app's handler — which relies on `data.shop` (per the library's own contract, `WebhookMetadata#shop`) as the tenant key for storage/lookup — will process or store the attacker's chosen payload under a victim shop's identity. This is a cross-tenant data-integrity/confidentiality break (Critical, per the in-scope impact categories) achievable purely through this gem's own webhook-processing API, not by the host app ignoring documentation — the gem's own `Request`/`Registry.process` contract is what fails to bind `shop` to the signature.

### Likelihood Explanation
High. No secret material is needed. Any developer can build a free Shopify dev store, install the target app, capture one legitimately delivered webhook (any topic they can trigger, e.g. `app/uninstalled` or any subscribed topic), and replay it with a modified header using a trivial HTTP client. The only prerequisite is that the target app is a public/installable app, which is the normal deployment model for apps built on this gem.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the signed material, or otherwise cryptographically bind the header-derived `shop` before it is trusted:
- At minimum, do not treat `request.shop` as verified tenant identity for authorization decisions unless it is cross-checked against a shop the app has confirmed installed/owns a session for.
- Prefer deriving trust for `shop` from a value covered by the signature (e.g., embedding `shop` in a signed envelope) rather than an arbitrary header, mirroring the fix pattern from the referenced report: stop trusting a value that participates in an action but is excluded from the integrity check, and add an explicit mismatch check between the header value and any independently-verified shop context before dispatching to `handler.handle`.

### Proof of Concept
1. Attacker installs the target Shopify app on their own dev store `attacker.myshopify.com`, and registers/receives a webhook (e.g. `orders/create`) at their configured endpoint.
2. Attacker captures the raw POST: body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(secret, B)` — this is valid because it was produced by Shopify using the app's real `api_secret_key`.
3. Attacker resends the identical request to the app's webhook endpoint, keeping `body = B` and `x-shopify-hmac-sha256 = H` unchanged, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Utils::HmacValidator.validate` recomputes HMAC over `B` only (per `to_signable_string`) and matches `H`, so validation succeeds: [8](#0-7) 
5. `Registry.process` dispatches to the handler with `shop: request.shop == "victim-shop.myshopify.com"`, even though the payload/body actually originated from and was signed for the attacker's own shop: [9](#0-8) 
6. The app processes attacker-chosen data as if it belongs to `victim-shop.myshopify.com`, achieving cross-tenant data injection/corruption.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
