## Title
Webhook shop-domain identity spoofing via header/HMAC binding gap — cross-tenant webhook confusion (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the **raw body**, then hands the caller-supplied `shop-domain` header straight through to the app's handler as the authoritative tenant identifier. The `shop` field is never covered by the HMAC that is verified, so it is a field that is *acted on* (used to identify which merchant/tenant the payload belongs to) but not *bound* by the cryptographic check that gates processing.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` values are all pulled straight from HTTP headers, independent of the signed payload: [2](#0-1) 

`Registry.process` validates only the HMAC of the request (i.e., the raw body against the app's `api_secret_key`), and then forwards `request.shop` unchanged to the handler as the identity of the merchant the payload is attributed to: [3](#0-2) 

Because `HmacValidator.validate_signature` computes the digest only from `verifiable_query.to_signable_string` (i.e., the raw body for webhooks) and compares it with `OpenSSL.secure_compare`, the header carrying `shop-domain` is completely outside the authenticated envelope: [4](#0-3) 

**Equality that should hold but doesn't:** `shop header used to attribute the event == shop that produced/authorized the signed body`. Since the HMAC only binds `raw_body ↔ api_secret_key`, any request with a body+HMAC pair that validates (e.g., one legitimately obtained from a webhook fired against the attacker's own installed/dev shop) can be replayed with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header changed to an arbitrary victim shop domain string. `Registry.process` will still consider the HMAC valid (it never looks at the header) and will call the handler with `WebhookMetadata.shop` set to the attacker-chosen value.

### Impact Explanation
Any application built on this gem that trusts `WebhookMetadata#shop` (as documented/intended — it's the only shop identifier exposed by this API) to route persisted state (order status, inventory, uninstall/GDPR actions, billing, etc.) to a specific tenant record is exposed to cross-tenant data confusion: an attacker who can obtain one valid (body, HMAC) pair for any shop (including their own, low-privilege store) can cause the app to process/attribute that payload against a different shop, without ever possessing that shop's credentials. This lands squarely in "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires no credentials beyond the ability to (a) trigger or observe any single legitimate webhook delivery to the endpoint (trivial for an attacker with their own dev/trial store built on the same app) and (b) POST a modified request with the same raw body/HMAC but a different `shop-domain` header to the app's public webhook endpoint. The webhook endpoint is by design internet-reachable and unauthenticated apart from this HMAC check, so likelihood is high once one payload/HMAC pair is known.

### Recommendation
Bind the shop identity into the value that is actually authenticated. Either:
- Require and verify the `shop` header against the set of shops for which the app currently holds a valid session/access token before invoking the handler, or
- Where feasible, additionally verify the shop domain the request claims to be from against Shopify's known registration for that specific webhook id/topic (e.g., a server-side lookup) rather than trusting the raw header.

### Proof of Concept
1. Attacker installs the app on their own dev shop `attacker.myshopify.com` and triggers an event that fires a real webhook (e.g., `orders/create`), capturing the raw body and the `x-shopify-hmac-sha256` value Shopify sent.
2. Attacker POSTs this exact body + HMAC header to the app's webhook endpoint again, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `raw_body` [5](#0-4)  — validation succeeds because the body/secret pair is unchanged.
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: <attacker's data>, ...)` [6](#0-5) , causing the host application to process attacker-controlled data under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
