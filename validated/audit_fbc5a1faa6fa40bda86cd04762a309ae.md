### Title
Webhook shop-domain/topic/webhook-id headers are trusted by `Webhooks::Registry.process` without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `ShopifyAPI::Utils::HmacValidator.validate` only authenticates the JSON body of an incoming webhook, never the `shop`, `topic`, `webhook_id`, or `api_version` values that the gem reads straight from HTTP headers. `Webhooks::Registry.process` accepts the request purely on the strength of that body-only HMAC check and then hands the *unauthenticated* header-derived `shop`/`topic`/`webhook_id` values to the app's handler as trusted metadata.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are read verbatim from HTTP headers with no cryptographic tie to the signed body: [2](#0-1) 

`HmacValidator.validate` computes and compares the HMAC solely over `verifiable_query.to_signable_string` (i.e. the raw body): [3](#0-2) 

`Registry.process` gates the entire flow on that body-only check and then forwards the header-sourced, unauthenticated `shop` (and `topic`/`webhook_id`) straight to the registered handler as `WebhookMetadata`: [4](#0-3) 

The identity binding that should hold is: `shop header used by the handler == shop that produced/authorized the signed body`. Instead, the code only verifies `hmac(raw_body, api_secret_key) == received_hmac`; it never binds `shop`/`topic`/`webhook_id` into that signature. Any unprivileged internet user who can obtain one legitimately-signed `(raw_body, hmac)` pair for the app - trivially achievable by installing the same app for free on a shop they control and capturing a real webhook delivery - can replay that exact body+HMAC to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (and/or `x-shopify-topic`/`x-shopify-webhook-id`) header. `Registry.process` will treat this as a fully valid, HMAC-verified webhook and dispatch it to the app's handler tagged with the attacker-chosen `shop`, `topic`, and `webhook_id` values, since none of those fields are checked against the signature.

### Impact Explanation
This breaks the tenant/shop identity binding for every app using `ShopifyAPI::Webhooks::Registry`: an attacker who owns any shop where the app is installed can forge webhook events that the app's handler will process as originating from a *different* merchant (`data.shop`), or as a different topic/webhook_id than what was actually signed. Handlers that use `data.shop` to select which merchant's data/record to mutate (a common and expected pattern, since `WebhookMetadata#shop` exists specifically for that purpose) can be tricked into acting on/for another tenant using data the attacker fully controls (the body they captured, replayed under a spoofed shop). This is cross-tenant access achieved purely as an unprivileged internet user with no access token, no `api_secret_key`, and no privileged account - matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any attacker capable of installing the target app on a shop they control (a normal, unprivileged step available to any developer/merchant), since that is the only prerequisite for obtaining a legitimately HMAC-signed `(body, hmac)` pair. From there, forging the `shop-domain`/`topic`/`webhook_id` headers on a replayed HTTP POST to the app's public webhook endpoint requires no cryptographic material at all - the gem performs no server-side allow-list check that the `shop` header matches an installed/known shop, and no signature covers the header values.

### Recommendation
Bind the identity-critical headers into the HMAC verification (or otherwise independently authenticate them), for example by including `shop`, `topic`, and `webhook_id` in the signable string computed in `Request#to_signable_string`, or by requiring `Registry.process` to additionally verify that `request.shop` matches a known/installed shop before dispatching to the handler. Document to consumers that `WebhookMetadata#shop`/`#topic`/`#webhook_id` are not currently HMAC-authenticated so handlers must not treat them as trusted tenant identifiers on their own.

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled shop (`attacker-shop.myshopify.com`) and trigger any webhook event the app subscribes to (e.g. `orders/create`). Capture the raw request body and the `x-shopify-hmac-sha256` header Shopify sent - both are validly signed with the app's shared `api_secret_key`.
2. Replay an HTTP POST to the app's public webhook endpoint using the exact captured `raw_body` and `x-shopify-hmac-sha256`, but replace `x-shopify-shop-domain` with `victim-shop.myshopify.com` (and optionally change `x-shopify-topic`/`x-shopify-webhook-id`).
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses the forged headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only hashes `raw_body`: [5](#0-4) 
4. The handler registered for that topic is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: request.parsed_body, ...)`: [6](#0-5) 
   causing the app to process attacker-supplied data under the identity of a shop the attacker never installed the app on or authenticated as.

### Citations

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
