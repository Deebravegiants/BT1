### Title
Webhook `shop` identity is not bound to the HMAC, allowing cross-tenant shop spoofing via header substitution - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body [1](#0-0) , while `Registry.process` treats `request.shop` (derived from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header) as a trusted identity when dispatching the webhook to the handler [2](#0-1) . The HMAC only proves the body was signed with the app's shared `api_secret_key`; it never binds that signature to the `shop` value that accompanies the request.

### Finding Description
`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string`, and for webhook requests that value is `@raw_body` only [3](#0-2) [4](#0-3) . The `shop`, `topic`, and `webhook-id` headers are read straight from `@headers` without any cryptographic coverage [5](#0-4) .

`Registry.process` gates only on the HMAC check, then forwards `request.shop` unmodified to the app's handler as an authenticated field via `WebhookMetadata`: [2](#0-1) 

The identity binding broken here is: `shop authenticated by HMAC == shop claimed in header`. In fact, `api_secret_key` is a single shared secret for the whole app across all installed shops (not per-tenant), so any tenant that legitimately receives one authentic webhook (with a valid HMAC over its raw body) possesses a `(raw_body, hmac)` pair that will validate successfully regardless of which `shop` header accompanies it. A malicious merchant who has installed the app can:
1. Receive a legitimate webhook for their own shop (`shop-A`), capturing `raw_body` and its valid `hmac-sha256` header.
2. Replay the exact same `raw_body`/`hmac` pair to the app's webhook endpoint, but substitute `x-shopify-shop-domain: shop-B.myshopify.com`.
3. `HmacValidator.validate` still succeeds because it never inspects the `shop` header, and `Registry.process` calls the handler with `WebhookMetadata.new(shop: "shop-B.myshopify.com", ...)`.

If the consuming application uses `data.shop` to select which tenant's session/access token/state to act on (the documented and expected use, per the gem's own webhook processing example) [6](#0-5) , this allows one tenant to inject fabricated webhook data attributed to a different tenant, i.e., a cross-tenant confusion primitive rooted entirely in this gem's verification logic (the field acted upon, `shop`, is never part of the signed payload).

### Impact Explanation
This breaks the identity binding "shop authenticated via HMAC vs. shop stored/acted upon" and results in cross-tenant data injection: a low-privilege but authenticated app-installer (any merchant who installs the app) can cause the app to process attacker-controlled webhook content under a victim shop's identity, without ever needing `api_secret_key`, an access token, or the victim's credentials — only their own legitimately-received webhook payloads and forged HTTP headers to the app's own webhook endpoint. This is a cross-tenant access primitive as defined by the rules (Critical bucket) because it lets one tenant impersonate/pollute another tenant's webhook stream at the application layer.

### Likelihood Explanation
Likelihood is high in the specific sense that no secret material is required — only capturing one's own legitimately-delivered webhook body/HMAC and re-sending it with a different `shop` header directly to the app's public webhook endpoint. It requires the attacker to be an installed merchant of the target app (or otherwise capable of triggering delivery of an authentic webhook to themselves), which is a normal, unprivileged usage path, not a privileged internal action.

### Recommendation
Bind the claimed `shop` (and ideally `topic`/`webhook-id`) into the HMAC-verified data, e.g., by including the `x-shopify-shop-domain` header value in `to_signable_string`, or by cross-checking `request.shop` against an out-of-band trusted mapping (e.g., the session/shop record the webhook subscription was registered for) before invoking the handler. At minimum, document prominently that `WebhookMetadata#shop` is *not* cryptographically authenticated by `Registry.process` and must be independently verified by the consuming application before being used to select tenant state.

### Proof of Concept
```ruby
# Attacker owns/installed the app on shop-A.myshopify.com and legitimately
# receives a real webhook, capturing:
raw_body = '{"id":123,"note":"legit order update for shop-A"}'
valid_hmac = Base64.encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), app_secret, raw_body)
) # attacker does NOT know app_secret but Shopify computed this for them

# Attacker replays the identical body+hmac, but swaps the shop header:
forged_headers = {
  "x-shopify-topic" => "orders/updated",
  "x-shopify-hmac-sha256" => valid_hmac,       # unchanged, still valid
  "x-shopify-shop-domain" => "shop-B.myshopify.com", # victim shop, forged
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) => true, because it only checks raw_body
# Handler is invoked with WebhookMetadata(shop: "shop-B.myshopify.com", ...)
# even though the payload never originated for shop-B.
``` [2](#0-1)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
