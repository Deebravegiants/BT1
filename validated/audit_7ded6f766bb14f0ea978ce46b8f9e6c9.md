This confirms the finding: the gem's documented API explicitly tells app developers "This will verify the request did indeed come from Shopify" (`docs/usage/webhooks.md` line 125), and passes `data.shop` to the handler as an authenticated field — but the `shop` (and `topic`, `webhook_id`, `api_version`) values are read from HTTP headers that sit entirely outside the HMAC's coverage.

### Title
Webhook `shop-domain` (and `topic`/`webhook_id`/`api_version`) headers are trusted for tenant routing but are not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authenticated once `Utils::HmacValidator.validate(request)` succeeds, and then forwards `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` to the app's handler as trusted, Shopify-attested values. However, `Webhooks::Request#to_signable_string` returns only the raw body — none of the header-derived fields are part of the signed content, so the binding `hmac == HMAC(secret, shop ‖ topic ‖ body)` that the app relies on does not actually hold; only `hmac == HMAC(secret, body)` is enforced.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes the expected signature from `verifiable_query.to_signable_string` and compares it to the `hmac` field: [1](#0-0) 

For webhooks, `Webhooks::Request` implements `VerifiableQuery` with: [2](#0-1) 

`to_signable_string` returns only `@raw_body` (line 37), while `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers (`shopify_header`) without any cryptographic tie to the signature.

`Registry.process` checks the HMAC and then immediately hands the header-derived `shop` to the handler as if it were verified: [3](#0-2) 

The gem's own documentation instructs developers to treat `data.shop` (and the other header-derived fields) as authenticated identifiers to key their tenant data: [4](#0-3) [5](#0-4) 

Because the equality `hmac == HMAC(secret, shop, topic, body)` is never actually checked — only `hmac == HMAC(secret, body)` is — an unprivileged internet user who installs the target app on their own store receives genuinely Shopify-signed webhook deliveries for their own shop (`raw_body` + valid `hmac`). They can then replay that exact `raw_body`/`hmac` pair to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header (and/or `X-Shopify-Topic`) with a victim shop's domain. `HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` will invoke the app's handler with `data.shop` set to the victim's domain and `data.body` set to attacker-controlled content, causing the host application to attribute attacker-controlled data to another tenant.

### Impact Explanation
This breaks the tenant boundary (`shop` identity) that all consuming apps (e.g., via the `shopify_app` gem's documented pattern) rely on to route webhook payloads to the correct merchant's data store. An attacker can inject or misattribute webhook content (including sensitive topics such as `app/uninstalled`, `shop/redact`, `customers/data_request`, or order/product mutations) under an arbitrary victim shop domain of their choosing, since nothing in the gem enforces that the header-declared shop matches the entity that produced the signed body. This is a cross-tenant integrity/access violation in a multi-tenant app built on this gem's documented webhook-processing contract.

### Likelihood Explanation
Requires only that the attacker be able to install the target app on a shop they control (standard for any public/unlisted Shopify app) and send a crafted HTTP request to the app's public webhook endpoint — no access to the app's `api_secret_key`, TLS interception, or privileged account is needed. The bug is a straightforward missing-binding: the values acted upon (`shop`, `topic`, `webhook_id`, `api_version`) are never part of the signed payload.

### Recommendation
Include the identifying headers (`shop`, `topic`, `webhook_id`, `api_version`) in the value that is HMAC-verified, or otherwise cryptographically/independently bind them to the request (e.g., verify `shop` against the session/shop the webhook was registered for, and/or require the gem's `Request#to_signable_string` to canonically include these header fields so the signature check in `HmacValidator.validate` actually covers them).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and registers/receives a real webhook, capturing the raw request body `B` and the corresponding `X-Shopify-Hmac-Sha256` header `H` (valid, since Shopify signs it with the app's real secret).
2. Attacker sends a new HTTP request to the app's public webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `X-Shopify-Hmac-Sha256: H` (unchanged)
   - Header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (changed)
   - Header `X-Shopify-Topic`: unchanged or changed to another registered topic
3. `ShopifyAPI::Utils::HmacValidator.validate` recomputes HMAC over `@raw_body` only [6](#0-5)  — it matches `H`, so validation passes.
4. `Registry.process` calls the app's handler with `data.shop == "victim-shop.myshopify.com"` [7](#0-6) , and the host app processes/stores the attacker's webhook body as if it originated from the victim shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

**File:** docs/usage/webhooks.md (L10-16)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
```

**File:** docs/usage/webhooks.md (L123-135)
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
