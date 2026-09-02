### Title
Webhook HMAC Only Signs the Raw Body, Not the `shop-domain`/`topic` Headers, Allowing Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while the `shop`, `topic`, `webhook_id`, and `api_version` values consumed by `ShopifyAPI::Webhooks::Registry.process` are all pulled unauthenticated from HTTP headers. The HMAC verification therefore proves nothing about which shop or topic a webhook claims to be for — only that *some* body byte-string was signed with the app's secret at some point. This breaks the identity binding `shop authenticated by HMAC == shop the app acts on`.

### Finding Description
`Registry.process` validates a webhook purely via `Utils::HmacValidator.validate(request)`: [1](#0-0) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`: [2](#0-1) 

For webhook requests, `to_signable_string` is defined to be the raw body only: [3](#0-2) 

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are read directly from client-supplied headers (`shopify-shop-domain`, `shopify-topic`, etc.) and are **not** part of the signed payload: [4](#0-3) 

These header-derived, unauthenticated values are then forwarded directly to the app's webhook handler as the tenant identifier: [5](#0-4) 

The equality that should hold is:
`shop bound by the HMAC signature == shop the handler is told the event belongs to`

Instead, the gem enforces only `HMAC(body) == valid` and separately trusts `headers["shop-domain"]` verbatim, so the two are completely decoupled. Anyone who can obtain one valid `(raw_body, hmac)` pair signed by the app's real secret — trivially achievable by installing the target app on a shop they themselves control and capturing a real Shopify-sent webhook — can replay that exact body/hmac pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value for a *different* (victim) shop. `HmacValidator.validate` will still return `true` because it never inspects headers, and `Registry.process` will hand the handler a `WebhookMetadata` whose `shop` is the attacker-chosen value.

### Impact Explanation
This is a cross-tenant identity confusion at the gem level: the library provides no verified binding between the cryptographically-authenticated bytes (body only) and the `shop` value applications are expected to trust as the tenant scope for processing the webhook (e.g., deciding which shop's data to update/delete, which access token/session to load, etc.). Any host application that follows this gem's documented webhook-processing API (`Registry.process` → `handler.handle(data:)`) inherits the flaw, since the gem itself is the one asserting authenticity via `Utils::HmacValidator.validate(request)` and then supplying an unauthenticated `shop`. This falls under cross-tenant access.

### Likelihood Explanation
Any actor who can install (or has already installed) the target app on a shop under their control — i.e., an ordinary unprivileged merchant/internet user, no leaked credentials or `api_secret_key` needed — can capture at least one legitimately-signed `(body, hmac)` pair from Shopify and replay it with a forged `shop-domain` header to the app's own public webhook endpoint. No knowledge of the app's `client_secret`/`api_secret_key` is required to perform the header substitution, only to have triggered one real webhook on their own store previously.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) as part of the signed input verified by `HmacValidator`, or otherwise cryptographically bind the header-derived `shop` to the authenticated body (e.g., require the shop to be independently confirmed against a known/installed shop record before trusting it, and never treat header values as authenticated solely because the body HMAC checked out). At minimum, `ShopifyAPI::Webhooks::Request#to_signable_string` should not be the only trust anchor used to authorize which shop a webhook is attributed to.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a shop they own) and triggers a webhook event (e.g. `app/uninstalled`), letting Shopify deliver a legitimately HMAC-signed request:
   - headers: `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`
   - body: `RAW_BODY`
2. Attacker replays the captured `RAW_BODY` and `x-shopify-hmac-sha256` value to the same app endpoint, but swaps the header:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
3. `ShopifyAPI::Webhooks::Request.new` parses these headers unchanged; `Utils::HmacValidator.validate(request)` recomputes HMAC over `RAW_BODY` only and it matches, since the body was untouched.
4. `Registry.process` invokes `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...))`, causing the app to process/act on the request as if it originated from `victim-shop.myshopify.com`, despite the byte-signature only proving authenticity for the attacker's own shop's payload.

### Citations

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
