Based on my analysis, I've confirmed a valid analog vulnerability in the webhook verification path.

### Title
Webhook `shop` header is not covered by the HMAC signature, allowing cross-tenant webhook forgery/replay - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats an incoming webhook as authenticated for a given shop as soon as `Utils::HmacValidator.validate(request)` succeeds, then forwards `request.shop` — a value taken verbatim from the unauthenticated `x-shopify-shop-domain` HTTP header — to the app's handler as the trusted tenant identifier. The HMAC that is actually verified only ever covers the raw request body, and is computed with the single, app-wide `Context.api_secret_key` that is identical for every shop that installs the app. The shop domain is never part of the signed material.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate`/`validate_signature` compute the HMAC purely over `verifiable_query.to_signable_string` (i.e. the raw body) using the app's global `Context.api_secret_key` (the same secret is used regardless of which shop the webhook claims to be from): [2](#0-1) 

`Registry.process` gates entirely on this body-only HMAC, and then trusts `request.shop` (the header value) as the tenant identifier passed to the app's handler: [3](#0-2) 

`request.shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cross-check against the HMAC-signed body: [4](#0-3) 

The resulting `WebhookMetadata.shop` is documented and expected to be used by app authors as the trusted tenant key for processing the webhook (e.g. to look up sessions, delete data for `shop/redact`, etc.): [5](#0-4) [6](#0-5) 

**Broken equality:** the shop whose secret was used to validate the HMAC (none in particular — it's the app's single global secret) is treated as equal to "the shop the app should act on" (`request.shop`, an unauthenticated header). Because the secret is shared across all shops using the app, and the shop identity is not part of the signed payload, any body+HMAC pair that is valid for one shop is equally "valid" (per this validator) for a header claiming to be any other shop.

### Impact Explanation
An unprivileged internet user can:
1. Install the target app on their own store (a normal, unprivileged action available to anyone), triggering any registered webhook topic (e.g. `customers/redact`, `shop/redact`, `orders/create`) so Shopify sends a legitimately signed webhook to the app's public HTTP endpoint.
2. Capture that raw body and its `x-shopify-hmac-sha256` value.
3. Replay the exact same body/HMAC pair to the app's webhook endpoint, but substitute the `x-shopify-shop-domain` header with a victim shop's domain.
4. `Utils::HmacValidator.validate` still passes (it never inspected the shop header or bound it to the secret), and `Registry.process` invokes the app's handler with `WebhookMetadata.shop` set to the victim's domain.

This lets an attacker forge cross-tenant webhook events for arbitrary shops using the app — e.g. triggering a false `shop/redact`/`customers/redact` GDPR-compliance handler against a victim's data, or injecting spoofed business events attributed to a victim shop — without ever needing the app's `client_secret`, an access token, or TLS interception. This is a cross-tenant access issue.

### Likelihood Explanation
Likelihood is high for any app that is installable by the public (most Shopify apps are) and that has webhook handlers whose logic branches meaningfully on the reported `shop` value. No credentials beyond the ability to install the app on one's own store are required, and webhook endpoints are typically public HTTP routes.

### Recommendation
Do not trust the header-supplied shop domain as authenticated. Options:
- Bind the shop to the signed material — verify the reported shop against a shop known from a prior authenticated context (e.g. only accept `shop/redact` etc. for shops with an active, previously-established session/webhook registration record) before invoking the handler.
- Alternatively/complementarily, look up the expected topic-specific handler behavior keyed by an internal record of which shops are installed, rather than trusting `request.shop` unconditionally, and treat the header as merely a routing hint, not an authenticated tenant identifier.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`.
2. App registers `customers/redact` webhook; Shopify sends `POST /webhooks` with body `B` and header `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, where `H = HMAC-SHA256(api_secret_key, B)`.
3. Attacker captures `B` and `H`.
4. Attacker sends `POST /webhooks` with the same body `B`, same header `x-shopify-hmac-sha256: H`, but `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `Utils::HmacValidator.validate` recomputes `HMAC-SHA256(api_secret_key, B)` — identical to `H` — and returns `true`.
6. `Registry.process` calls the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, and the app's business logic (e.g. redaction, reprovisioning) executes against `victim-shop.myshopify.com` based on attacker-controlled input.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L1-12)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Webhooks
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** docs/usage/webhooks.md (L10-18)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```
