This confirms the finding. The documentation explicitly states `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" (docs/usage/webhooks.md line 125), and instructs handlers to trust `data.shop` as "The shop domain of the webhook" (line 14) and use it directly, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)` (line 26). But the HMAC verification only covers the raw body, not the shop-domain header.

### Title
Webhook shop-domain header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop` is read directly from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header [2](#0-1) . `Utils::HmacValidator.validate` computes the signature over `to_signable_string` only [3](#0-2) , so passing HMAC validation proves the body was signed with the app's `api_secret_key`, but proves nothing about which shop the header claims to be from.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` raises unless `Utils::HmacValidator.validate(request)` succeeds, then immediately builds `WebhookMetadata` using `request.shop`, which is taken from the header, and forwards it to the app-provided handler unmodified [4](#0-3) . Because the `api_secret_key` is the app's single shared client secret used for *every* installed shop (not a per-shop key), any unprivileged attacker who has installed the app on their own shop can:

1. Trigger a real webhook from Shopify to their shop (or otherwise obtain a body + valid `hmac-sha256` header pair).
2. Replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary victim shop domain in the `x-shopify-shop-domain` header.

`Utils::HmacValidator.validate` still returns `true`, because the signature check never inspects the shop header — it only checks `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)` [5](#0-4) . The identity binding broken here is: `shop_verified_by_HMAC == shop_delivered_to_handler`. In reality no such binding exists — the gem verifies only the *body's* authenticity, while `data.shop` is fully attacker-controlled.

This is a materially different situation from Shopify's own webhook delivery guarantee, and the gem's own documentation misrepresents the property: it states processing "will verify the request did indeed come from Shopify" and instructs developers to trust `data.shop` as the shop domain of the webhook [6](#0-5) , encouraging exactly the vulnerable pattern of keying off `data.shop` for tenant-scoped work [7](#0-6) .

### Impact Explanation
An unprivileged attacker (any merchant who can install the app, or anyone who has captured a single legitimate webhook body/HMAC pair) can forge webhook deliveries that the gem will report as HMAC-verified for an arbitrary victim shop domain of their choosing. Any host application that follows the documented pattern of using `data.shop` to select/update per-tenant records (the exact example shown in the gem's own docs) is exposed to cross-tenant data corruption or disclosure driven entirely by this gem's mis-scoped verification — the gem asserts an identity guarantee (`shop` is authenticated because HMAC passed) that it does not actually provide.

### Likelihood Explanation
High likelihood of exploitation for any app relying on the documented `data.shop` pattern: the attack requires no privileged credentials, no access token, and no secret — only a single legitimate webhook body/signature pair (trivially obtainable by installing the app on an attacker-owned shop) and the ability to POST to the app's public webhook endpoint with custom headers.

### Recommendation
Include the shop domain (and ideally other identifying headers such as topic/webhook-id/api-version) inside the HMAC-covered signable string, or independently verify `shop` against a value the app already trusts (e.g., a per-shop secret, or cross-check against an existing session/webhook subscription record) before constructing `WebhookMetadata`. At minimum, update the documentation to make clear that `data.shop` is not authenticated by the HMAC check and must not be trusted for tenant selection without additional verification.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; capture one legitimate webhook: raw body `B` and header `x-shopify-hmac-sha256: H` (valid for the app's shared `api_secret_key`).
2. POST to the app's webhook endpoint with:
   - `raw_body`: `B` (unchanged)
   - `x-shopify-hmac-sha256`: `H` (unchanged)
   - `x-shopify-shop-domain`: `victim.myshopify.com` (attacker-chosen)
   - `x-shopify-topic`, `x-shopify-webhook-id`, `x-shopify-api-version`: copied/forged as needed.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` [8](#0-7) , which succeeds because it only re-hashes `B` against the shared secret.
4. The registered handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` and, following the documented usage pattern, performs tenant-scoped work keyed on the attacker-forged `shop` value [9](#0-8) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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

**File:** docs/usage/webhooks.md (L10-16)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
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
