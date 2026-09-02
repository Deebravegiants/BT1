Confirmed: the interface confines what's cryptographically covered to `to_signable_string`, and for webhooks that's the raw body only [1](#0-0) , while the `shop`, `topic`, `webhook-id`, and `api-version` fields consumed downstream come straight from unauthenticated HTTP headers [2](#0-1) .

### Title
Webhook `shop`, `topic`, `webhook-id`, and `api-version` fields are trusted without HMAC coverage, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook request solely by recomputing the HMAC over the raw request body, then dispatches to the app's handler using `request.shop`, `request.topic`, and `request.webhook_id` — none of which are covered by that HMAC. Any party who can obtain one validly-signed `(raw_body, hmac)` pair for the shared app secret (e.g., by installing the app on their own free/dev store and capturing a real webhook delivery) can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting arbitrary values for the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers. `Registry.process` will accept it as authentic and hand the attacker-chosen `shop` value to the app's handler as if it originated from that shop.

### Finding Description
`Registry.process` gates on HMAC validity only: [3](#0-2) 

`HmacValidator.validate` computes/compares the signature strictly against `verifiable_query.to_signable_string`: [4](#0-3) 

For `Webhooks::Request`, `to_signable_string` returns only the raw body (`@raw_body`), never the headers: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from attacker-controllable HTTP headers with no cryptographic tie to the signed body: [2](#0-1) 

This breaks the binding that should hold: `shop_that_HMAC_covers == shop_that_handler_acts_on`. In reality, `shop_that_HMAC_covers = ∅` (only body bytes are covered) while `shop_that_handler_acts_on = attacker_supplied_header`. The app's secret (`Context.api_secret_key`) is shared across every shop that has the app installed, so a genuine signature obtained from the attacker's own tenant is valid for any header combination they choose to send to the app's public webhook route — the gem provides no mechanism (and the docs' example controller in `docs/usage/webhooks.md` performs no additional check) to bind the header-derived `shop` to the signed bytes.

### Impact Explanation
This is a cross-tenant identity-binding break: an attacker who legitimately controls one shop with the app installed can cause the app to process a forged webhook "from" any other shop domain, topic, or webhook id of their choosing, while still passing `Registry.process`'s only integrity check. Depending on how the host app's registered handlers act on `WebhookMetadata#shop`/`#topic`/`#body` (e.g., updating merchant records, triggering shop-scoped side effects, or looking up/creating sessions keyed by the spoofed shop), this can lead to cross-tenant data corruption or unauthorized actions attributed to a shop the attacker does not control — satisfying the "cross-tenant access" impact category.

### Likelihood Explanation
Requires only: (1) the ability to install the target app on any shop (a normal, unprivileged action any merchant/developer can do, including free/dev stores), (2) capturing one legitimate webhook delivery to obtain a valid `(raw_body, hmac)` pair, and (3) sending a direct HTTP POST to the app's public webhook endpoint with forged `x-shopify-shop-domain`/`x-shopify-topic`/`x-shopify-webhook-id` headers. No access token, `client_secret`, or privileged credential is needed — the attacker only needs their own legitimately-issued webhook.

### Recommendation
Bind the headers that the handler relies on into the signature verification, or otherwise cryptographically/authoritatively confirm that the `shop-domain` (and ideally `topic`/`webhook-id`) header matches the shop for which the raw body was actually signed — e.g., by cross-checking against Shopify's own webhook delivery metadata (which Shopify signs end-to-end per delivery) rather than trusting the header value on its own. At minimum, document prominently that `Request#shop`/`#topic`/`#webhook_id` are unauthenticated and must not be used for tenant-scoping decisions without independent verification.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker.myshopify.com` and lets it register a webhook (e.g., `orders/create`).
2. Shopify delivers a legitimately-signed webhook to the app's endpoint with body `B` and header `x-shopify-hmac-sha256: H` (valid for secret `S` shared by the app across all installs) and `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker captures `B` and `H`, then sends a new POST directly to the same app endpoint with identical body `B` and header `H`, but with `x-shopify-shop-domain: victim.myshopify.com` and/or a different `x-shopify-topic`.
4. `Registry.process` calls `HmacValidator.validate(request)`, which recomputes HMAC over `B` only and finds it matches `H` — validation passes: [5](#0-4) 
5. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim.myshopify.com", body: ..., ...)`, i.e., the app processes an event as if it originated from `victim.myshopify.com`, even though nothing about that shop was ever cryptographically verified.

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
