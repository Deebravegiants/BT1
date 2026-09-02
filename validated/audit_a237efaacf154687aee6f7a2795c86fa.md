### Title
Webhook shop/topic/API-version attribution is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` only includes the raw request body in the HMAC-signable string. The `shop-domain`, `topic`, `webhook-id` and `api-version` headers are read directly from unauthenticated HTTP headers and handed to the registered handler without ever being covered by the HMAC check, breaking the identity binding between "HMAC-verified bytes" and "shop the event is attributed to."

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

All other identifying fields — `shop`, `topic`, `webhook_id`, `api_version` — are pulled straight from HTTP headers with no cryptographic binding: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC over exactly `verifiable_query.to_signable_string` (i.e. only the body) using `Context.api_secret_key`, and compares it against the `hmac-sha256` header: [3](#0-2) 

`Registry.process` gates on this HMAC check and then constructs the metadata handed to the app's handler directly from the request's unauthenticated `shop`, `topic`, `webhook_id`, and `api_version` accessors: [4](#0-3) 

The broken identity binding, stated as an equality that the gem fails to enforce:
`bytes verified by HMAC (raw_body only)` ≠ `bytes actually used to attribute the event (shop-domain / topic / webhook-id / api-version headers)`.

Since the app's `api_secret_key` is a single shared secret used for every shop/topic combination on that app (not scoped per shop or per topic), any party who can obtain one valid `(raw_body, hmac)` pair — for instance, by legitimately installing the app on a shop they control and capturing a real webhook delivery, or by knowing/guessing a body that produces a payload of interest — can resend that exact body/HMAC pair while freely rewriting the `x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`, and `x-shopify-api-version` headers. `HmacValidator.validate` will still return `true` because it never inspects those headers, and `Registry.process` will invoke the topic handler with attacker-chosen `shop`/`topic` metadata even though the HMAC provides no guarantee that this body was ever produced for that shop or topic.

### Impact Explanation
This is a cross-tenant identity confusion: the gem lets an attacker cause a webhook handler to run believing the (verified) payload originated from an arbitrary shop or topic of the attacker's choosing. Any app logic that trusts `WebhookMetadata#shop` (or `#topic`) to key data lookups, provisioning/deprovisioning actions (e.g. `app/uninstalled`), or cross-tenant data writes can be manipulated into acting on/for the wrong tenant using a payload the attacker fully controls the framing of. This matches the Critical "cross-tenant access" impact category, since it lets one tenant (or an unprivileged party who once installed the app) forge the shop attribution of processed webhook events for other shops.

### Likelihood Explanation
Likelihood is Medium-High. The attacker only needs a single valid `(body, x-shopify-hmac-sha256)` pair for the shared `api_secret_key`, which is trivially obtainable by installing the target app themselves (a normal, no-privilege action for any Shopify merchant) and capturing one legitimate webhook delivery. The `shop-domain`, `topic`, `webhook-id`, and `api-version` headers can then be freely rewritten and resent to the app's webhook endpoint since nothing in this gem's HMAC verification path checks them.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the HMAC-signable string (or otherwise cryptographically bind them, e.g. by validating them against Shopify's out-of-band webhook metadata/registration records) rather than trusting raw headers. At minimum, document that these fields are unauthenticated and instruct integrators not to make trust decisions based on `WebhookMetadata#shop`/`#topic` without independent verification (e.g., confirming the shop has an active session/installation and that the topic matches an actively registered subscription for that specific shop).

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled development store; trigger a webhook event (e.g. `orders/create`) so Shopify delivers a genuine `(raw_body, x-shopify-hmac-sha256)` pair signed with the app's shared `api_secret_key`.
2. Capture that raw body and HMAC value.
3. Send a forged HTTP request to the app's webhook endpoint using the captured `raw_body` and `x-shopify-hmac-sha256` unchanged, but replace `x-shopify-shop-domain` with a victim shop's domain (any shop that also has the app installed) and/or replace `x-shopify-topic`/`x-shopify-webhook-id` with different values.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate` returns `true` because it only checks `raw_body` against the HMAC.
5. `ShopifyAPI::Webhooks::Registry.process` looks up the handler for the (attacker-chosen) `topic` and invokes it with `shop:` set to the victim's domain — the app's business logic now processes attacker-controlled data as if it legitimately originated from the victim shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
