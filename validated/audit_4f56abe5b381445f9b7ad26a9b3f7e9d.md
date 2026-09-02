## Title
Webhook shop/topic identity headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented as verifying "the request did indeed come from Shopify" before invoking the app's handler with a `shop` identity value. In reality, the HMAC signature validated by the gem only covers the raw request body — the `shop`, `topic`, `webhook_id`, and `api_version` values (all taken from unauthenticated HTTP headers) are never bound to that signature. An attacker who can produce (or replay) any single valid `body + hmac` pair for their own shop can freely relabel the `shopify-shop-domain` header to impersonate a different, victim shop when calling the app's webhook endpoint.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines the HMAC-signable content strictly as the raw request body: [1](#0-0) 

All identity fields the rest of the pipeline relies on — `shop`, `topic`, `webhook_id`, `api_version` — are pulled straight from HTTP headers that are not part of `to_signable_string` and therefore are not authenticated at all: [2](#0-1) 

`Utils::HmacValidator.validate` only checks `hmac` against `to_signable_string` (the body): [3](#0-2) 

`Registry.process` performs exactly this check and then hands `request.shop` (an unauthenticated header value) straight to the handler as the tenant identity: [4](#0-3) 

The documentation explicitly promises this call "will verify the request did indeed come from Shopify" and describes `data.shop` as "The shop domain of the webhook", i.e. an app-trusted tenant identifier: [5](#0-4) [6](#0-5) 

This breaks the intended binding `authenticated(body) == shop-identity-used-by-handler`. In practice: `hmac_valid(body) ⇏ shop-domain-header-is-authentic`, because the signature scope is `{body}` while the trust decision made by `Registry.process`/`WebhookMetadata` is `{shop, topic, webhook_id, api_version, body}`.

### Impact Explanation
Any actor who is themselves a legitimate merchant with the app installed (i.e., an "unprivileged internet user" relative to *other* merchants' data) receives genuine `body + shopify-hmac-sha256` pairs from Shopify for their own shop. Because the header carrying the shop domain is outside the signed content, that same valid signature can be replayed against the app's public webhook endpoint with the `shopify-shop-domain` (or `x-shopify-shop-domain`) header rewritten to any victim shop domain. The signature check still passes, and the app's `WebhookHandler#handle` receives `WebhookMetadata` claiming the event originated from the victim shop, while the body content is actually the attacker's own data. Depending on how the host app keys its per-shop data store off `data.shop` (which the gem's own documentation instructs apps to do), this enables cross-tenant data injection/confusion — data intended for shop A gets attributed and stored/processed under victim shop B's tenant record.

### Likelihood Explanation
High feasibility: no secret material is required beyond what any app-installing merchant already legitimately receives (a real webhook body/HMAC pair for their own shop). The only step is rewriting an HTTP header on replay, and both `Request` and `Registry.process` accept the doctored header without any cross-check against the signed body.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) in the value covered by the HMAC — matching Shopify's actual webhook signing intent — or, at minimum, have `Registry.process`/`WebhookMetadata` cross-validate the `shop` header against a shop value embedded/derivable from the verified body, and document clearly that header-derived fields are not currently authenticated so host apps do not use them as a trust boundary.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and configures a webhook (e.g. `orders/create`), so Shopify delivers a legitimate request to the app's webhook endpoint:
   - Headers: `shopify-shop-domain: attacker.myshopify.com`, `shopify-topic: orders/create`, `shopify-hmac-sha256: <valid HMAC of raw body B>`
   - Body: `B`
2. Attacker captures this raw body `B` and its valid HMAC (they can trigger this themselves at will, e.g. by placing test orders in their own store).
3. Attacker POSTs to the same public webhook URL with the identical body `B` and identical `shopify-hmac-sha256`, but changes `shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` succeeds because it only checks `body` vs `hmac` (`lib/shopify_api/webhooks/request.rb` `to_signable_string`, `lib/shopify_api/utils/hmac_validator.rb`).
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: <attacker's parsed body>, ...)`, causing the host app to process/store attacker-controlled data under the victim shop's tenant identity.

### Citations

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
