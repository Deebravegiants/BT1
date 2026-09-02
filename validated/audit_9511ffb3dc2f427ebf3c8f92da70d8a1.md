This confirms the finding. Let me verify the exact mechanics of `to_signable_string` for both `Request` and `AuthQuery` to be precise about what is/isn't covered by the HMAC.This confirms the analysis: for `AuthQuery` (OAuth), the `shop` field IS included in `to_signable_string`, so it's properly bound to the HMAC. But for `Webhooks::Request`, `to_signable_string` returns only `@raw_body` — the `shop` (and `topic`, `webhook_id`, `api_version`) fields are read from unsigned headers and are never part of the HMAC computation, yet `Registry.process` uses `request.shop` to build `WebhookMetadata` that host apps rely on to identify the tenant.

### Title
Webhook shop-domain identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers. `Registry.process` validates the HMAC over the body alone via `Utils::HmacValidator.validate`, then unconditionally trusts `request.shop` to construct the `WebhookMetadata` passed to the app's handler.

### Finding Description
`HmacValidator.validate` computes and compares the signature only against `verifiable_query.to_signable_string`: [1](#0-0) . For `Webhooks::Request`, `to_signable_string` is defined to return `@raw_body` exclusively — none of the Shopify headers are included: [2](#0-1) . The `shop`, `topic`, `webhook_id`, and `api_version` accessors are derived purely from HTTP headers that are never mixed into the signed string: [3](#0-2) .

`Registry.process` then does:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
  body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
``` [4](#0-3) 

This is the equality the gem is supposed to enforce: `hmac_verified(shop, body) == true` implies `shop` is authentic for that `body`. In reality the gem only enforces `hmac_verified(body) == true`, i.e. `shop` is asserted, not authenticated. Contrast this with `Auth::Oauth::AuthQuery`, where `shop` (and `host`, `code`, `state`, `timestamp`) IS included in `to_signable_string` and therefore is properly bound to the signature: [5](#0-4) . The webhook path lacks this same binding.

Because `shop` is not part of the signed material, an attacker who can obtain any one valid `(body, hmac)` pair signed with the app's `api_secret_key` for a given topic (e.g. by triggering/observing a legitimate webhook delivery to their own store, since store owners routinely have visibility into deliveries sent to endpoints they control) can replay that exact `body`/`hmac` combination while substituting an arbitrary value in the `x-shopify-shop-domain` (or `shopify-shop-domain`) header. `HmacValidator.validate` still returns `true` because it only checks the body, and `Registry.process` forwards the attacker-controlled `shop` value unchanged into `WebhookMetadata#shop`, which is the field host applications are documented to use for shop-scoped session/token lookups and job dispatch: [6](#0-5)  and [7](#0-6) .

### Impact Explanation
This breaks the tenant-identity binding the gem is expected to guarantee between an authenticated webhook body and the shop it is attributed to. A host application that (as documented) keys off `data.shop` to select the session/access-token or to route background jobs will process attacker-replayed data under an arbitrary victim shop domain, causing cross-tenant data confusion/injection within the app's own webhook processing pipeline. This matches the Critical "cross-tenant access" impact category, since the identity of the tenant the payload is attributed to is fully attacker-controlled once one valid signed body/hmac pair for the app is available.

### Likelihood Explanation
Likelihood is bounded by the fact that the attacker needs at least one genuinely-signed `(body, hmac)` pair for the target app — which is trivially available to anyone who installs the app on their own store and receives a real webhook delivery to their own endpoint (webhook delivery URLs and payloads are visible to the store owner who configured them, or can be intercepted at the receiving endpoint before/without needing `api_secret_key` itself). No possession of `api_secret_key`, access tokens, or refresh tokens is required — only re-emission of a header value (`shop-domain`) that is never covered by the signature.

### Recommendation
Include the `shop` (and ideally `topic`, `webhook_id`, `api_version`) values in the signed material for webhooks, mirroring what Shopify itself does for OAuth's `AuthQuery`. Since Shopify's actual webhook HMAC is computed over the raw body only (matching Shopify's server-side webhook signing), the safer fix is for `Registry.process`/`WebhookMetadata` to not present `shop` as a trusted, authenticated field on the same trust level as the body — or, at minimum, clearly document that `shop` is unauthenticated and must be independently verified (e.g., cross-checked against a known/registered shop for that webhook subscription) before being used for any session or token lookup.

### Proof of Concept
1. App receives a legitimate webhook from `attacker-shop.myshopify.com` for topic `orders/create` with body `B`, and a valid header `x-shopify-hmac-sha256: H` where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker replays the exact same request to the app's webhook endpoint, keeping body `B` and header `x-shopify-hmac-sha256: H` unchanged, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` returns `true`, since it only hashes `@raw_body` (`B`) — see [2](#0-1)  and [1](#0-0) .
4. `Registry.process` invokes the app's handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: B, ...)` — see [4](#0-3) .
5. The host application, following the gem's documented usage pattern of trusting `data.shop`, processes/enqueues the attacker's body `B` as if it genuinely originated from `victim-shop.myshopify.com`.

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

**File:** docs/usage/webhooks.md (L10-17)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
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
