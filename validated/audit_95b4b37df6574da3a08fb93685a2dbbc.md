### Title
Webhook HMAC signature does not cover the `shop-domain` header, allowing cross-tenant webhook shop-identity spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while the `shop` (and `topic`/`webhook_id`/`api_version`) values are read straight from unauthenticated headers. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC over the body only, then passes the header-derived `shop` value on to the caller's handler untouched, breaking the binding `shop authenticated == shop delivered to handler`.

### Finding Description
`Request#hmac` extracts the signature from the `hmac-sha256` header and `Request#to_signable_string` returns just `@raw_body`: [1](#0-0) [2](#0-1) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled from headers that are never part of the signed material: [3](#0-2) 

`Utils::HmacValidator.validate` only checks `verifiable_query.to_signable_string` (i.e., the raw body) against the computed HMAC using `Context.api_secret_key`: [4](#0-3) 

`Registry.process` validates only that HMAC, then forwards `request.shop` — an unauthenticated header value — straight into `WebhookMetadata` and the app's handler, without any further check that this shop is the one for which the signature was actually generated: [5](#0-4) 

Critically, the signing secret (`Context.api_secret_key`) is the app's single `client_secret`, shared across every shop that installs the app — it is not shop-specific. Because of this, the equality the gem should enforce is:

`shop bound to HMAC signature == shop delivered to handler`

but what is actually enforced is only:

`body bound to HMAC signature == body delivered to handler`

leaving `shop` (the tenant identifier) completely outside the cryptographic binding. This is precisely the "field acted on but not covered by the HMAC" pattern.

The library's own documentation states that `Registry.process` "will verify the request did indeed come from Shopify," which overstates the actual guarantee — it verifies the *body* came from Shopify for *some* installation of the app, not that the claimed `shop` is correct: [6](#0-5) 

### Impact Explanation
Because the HMAC secret is shared across all merchants of an app, any merchant who installs the app on their own store (an "unprivileged internet user" with respect to other tenants of the same app) can capture a legitimately-signed `(raw_body, hmac)` pair delivered to their own webhook endpoint, then replay that exact HTTP body/HMAC pair while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with a victim shop's domain. `Registry.process` will accept the HMAC (it only checks the body) and will invoke the host application's handler with `data.shop` set to the victim's shop domain, `data.topic`/`data.webhook_id` also attacker-controlled. Any host application that uses `data.shop` to key merchant records, trigger uninstall/GDPR flows, or otherwise treat this webhook as originating from that shop is now processing attacker-forged, cross-tenant webhook events. This is a cross-tenant identity confusion vulnerability directly attributable to the gem's `Request`/`Registry` design rather than misuse of a documented API — the gem markets `process` as verification "the request did indeed come from Shopify."

### Likelihood Explanation
Exploitation only requires the ability to install the target app on an attacker-controlled development store (readily available to any internet user via the Shopify Partners program) and the ability to POST an HTTP request to the app's public webhook endpoint with attacker-chosen headers — both are within reach of an unprivileged party. No access token, `api_secret_key`, or privileged account for the *victim* shop is required.

### Recommendation
Include the identity-critical headers (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed material (or otherwise cryptographically bind them, e.g. by verifying `shop` against a server-side registration for the webhook subscription) rather than trusting them as free-standing headers. At minimum, `Registry.process` should reject/flag mismatches between the claimed shop header and any independently-verifiable tenant context before invoking the handler, and the documentation should not claim full request-origin verification when only the body is authenticated.

### Proof of Concept
1. Attacker installs the target Shopify app on their own dev store `attacker.myshopify.com`, registers an `orders/create` webhook, and receives a legitimately Shopify-signed request at the app's webhook endpoint:
   - Headers: `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over BODY>`, `x-shopify-topic: orders/create`
   - Body: `BODY` (a valid, Shopify-signed JSON payload)
2. Attacker resends the exact same request to the app's webhook endpoint, changing only the `x-shopify-shop-domain` header to `victim-shop.myshopify.com`, keeping `BODY` and the `hmac-sha256` header untouched.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: BODY, headers: forged_headers)` is constructed by the host app exactly as documented: [7](#0-6) 
4. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only recomputes HMAC over `BODY`: [8](#0-7) 
5. The registered handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: parsed(BODY), ...)`: [9](#0-8) 
6. The host application processes this as a genuine `orders/create` event for `victim-shop.myshopify.com`, even though no such event occurred for that shop — a cross-tenant forgery enabled purely by the gem's failure to bind the `shop` field to the HMAC signature.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
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
