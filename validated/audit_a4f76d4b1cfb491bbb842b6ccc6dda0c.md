### Title
Webhook `shop` (and `topic`) identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the `shop` (and `topic`) values that the registry uses to route and attribute a webhook to a specific merchant are read from separate, unsigned HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC over the body only, then trusts the header-derived `shop`/`topic` to build the `WebhookMetadata` passed to the app's handler. This breaks the identity binding that should hold: `hmac_valid(body) ⇒ shop_is_authentic`. In fact `hmac_valid(body)` says nothing about `shop`, so a request with a valid signature for one payload can carry an attacker-chosen `shop`/`topic` header, and the handler will act as though the payload originated from that arbitrary shop.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
which only returns `@raw_body`. The `shop`, `topic`, `api_version`, and `webhook_id` accessors are all derived independently from HTTP headers that are never part of the signed data: [2](#0-1) 

`Registry.process` verifies the HMAC using `Utils::HmacValidator.validate(request)` (which signs/verifies `to_signable_string`, i.e. the body only), then immediately trusts `request.shop` and `request.topic` to build `WebhookMetadata` and dispatch to the registered handler: [3](#0-2) 

`HmacValidator.validate` only checks `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)`: [4](#0-3) 

The intended invariant is: *the HMAC over the bytes the gem verifies should bind the entire identity of the event (including which shop it came from)*. Instead, the bytes verified (`raw_body`) and the bytes used to determine tenant identity (`shopify-shop-domain` header) are disjoint. Any unprivileged actor who can obtain one genuine, validly-signed webhook body (e.g., by installing the app on their own free/dev store and receiving a real webhook from Shopify) can replay that exact body to the app's webhook endpoint with the `shopify-shop-domain` header (and/or `shopify-topic` header) changed to an arbitrary value. Because the signature check never inspects those headers, `Utils::HmacValidator.validate` still returns `true`, and `handler.handle` is invoked with `WebhookMetadata` claiming an attacker-chosen `shop`.

### Impact Explanation
This is a cross-tenant identity confusion: application logic that keys authorization, data storage, or side effects off `WebhookMetadata#shop` (the documented contract of this gem for webhook handlers) can be tricked into performing actions attributed to, or scoped to, a shop the attacker does not control. Since the app trusts the gem's HMAC validation as proof of authenticity for the whole event (including provenance), and the gem's validation does not actually bind `shop`, this satisfies the "cross-tenant access" criterion via a broken identity binding, analogous to the `L1Escrow` report's core issue of an operation being authorized/attributed based on unverified/uncovered data.

### Likelihood Explanation
Reaching this requires no credentials belonging to the target shop, no `api_secret_key`, and no privileged account — only a genuine webhook body from any shop (including the attacker's own store, or one observed some other way) and the ability to POST to the app's public webhook endpoint with modified headers. The signature check by design does not detect header tampering, so exploitation is straightforward for anyone who can obtain one valid signed body/topic pair.

### Recommendation
Include the shop domain (and topic, api version, webhook id if they influence behavior) inside the bytes covered by the HMAC verification — i.e., make `to_signable_string` bind the full identity tuple, not just the raw body — or otherwise cryptographically bind the `shopify-shop-domain`/`shopify-topic` headers to the signed payload before they are trusted for routing/attribution in `Registry.process`.

### Proof of Concept
1. Install the target app on an attacker-controlled shop (`attacker-shop.myshopify.com`) and capture a genuine webhook Shopify sends to the app, e.g. body `{"id":1}` with header `x-shopify-hmac-sha256: <validHmacForBody>` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Replay the exact same request to the app's webhook endpoint, but replace `x-shopify-shop-domain` with `victim-shop.myshopify.com` (and/or change `x-shopify-topic` to another registered topic), keeping the body and `x-shopify-hmac-sha256` unchanged.
3. `ShopifyAPI::Webhooks::Registry.process` computes:
   - `Utils::HmacValidator.validate(request)` → `true`, because `Request#to_signable_string` only returns `@raw_body`, which is unchanged.
   - `request.shop` → `"victim-shop.myshopify.com"`, from the tampered, unsigned header.
   - The handler runs with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)`, as shown in: [5](#0-4) 
   The app now processes an event as if it were authentic data from `victim-shop.myshopify.com`, despite the attacker never having any authorization tied to that shop.

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
