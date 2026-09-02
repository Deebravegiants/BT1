### Title
Webhook `shop-domain` header is trusted for tenant identification without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then hands the *unauthenticated* `shop-domain` header straight to the app's handler as the tenant identifier. Because the HMAC never covers the shop identity, any request bearing a body/HMAC pair that is valid for the app's secret can be replayed with an arbitrary `shop-domain` header, causing the host application to process the payload as belonging to a different, attacker-chosen shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` value used downstream is read from an entirely separate, unsigned header: [2](#0-1) 

`Registry.process` verifies the request using `Utils::HmacValidator.validate`, which only checks the HMAC over `to_signable_string` (i.e., the raw body) against the app's `api_secret_key`: [3](#0-2) [4](#0-3) 

The identity binding that should hold is:
`shop_that_produced_the_HMAC == shop_passed_to_handler`

but the code only proves:
`HMAC(secret, raw_body) == received_hmac`

The `shop`, `topic`, `webhook-id`, and `api-version` headers are never part of the signed material, so the equality above is never actually checked. Since Shopify signs webhooks with a single app-wide `api_secret_key` shared across all shops that install the app (there is no per-shop signing key or shop-bound HMAC input), a valid `(raw_body, hmac)` pair legitimately obtained from Shopify for shop A's own webhook traffic remains "valid" no matter which `shop-domain` header value accompanies it. `Registry.process` then dispatches the body to the handler tagged with whatever shop header the caller supplied: [5](#0-4) 

### Impact Explanation
An unprivileged user who has legitimately installed the target app on their own store (or otherwise obtained one authentic `(raw_body, hmac)` pair for any shop using the app) can replay that exact body to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with a victim shop's domain. Because the HMAC check never inspects the shop header, the request passes verification, and the host application's handler receives `WebhookMetadata` claiming the data belongs to the victim shop. Depending on the handler's logic (e.g., updating local records keyed by `shop`, triggering shop-scoped side effects, or acting on `data.shop` to select credentials/state), this results in cross-tenant data confusion/injection — writing or triggering shop-A-controlled content under shop-B's tenant record. This matches the Critical "cross-tenant access" impact category, since the trust boundary between tenants (shops) is defined entirely by this unauthenticated header.

### Likelihood Explanation
Likelihood is limited by the need for the attacker to first obtain at least one genuine `(body, hmac)` pair signed with the app's secret — which is straightforward for anyone who can install the app on their own shop and capture their own webhook deliveries (a normal, unprivileged action, not requiring the app's `client_secret`). Whether the confusion is exploitable in practice further depends on whether a given webhook body contains no shop-identifying content of its own and on how permissively the host app's handler trusts `data.shop`; the gem itself provides no safeguard against this and documents `shop` as an authoritative field of `WebhookMetadata`.

### Recommendation
Bind the shop identity to the authenticated material: e.g., require callers to also verify that the `shop-domain` header matches a shop with an active, previously stored session/installation before dispatching to handlers, or extend the signable string / verification step so the shop domain is validated against known installed shops rather than being trusted as an unauthenticated header. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must be cross-checked by the host app against its own shop/session store before use.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and captures one legitimate webhook delivery, e.g.:
   ```
   POST /webhooks
   x-shopify-topic: products/update
   x-shopify-hmac-sha256: <valid-hmac-for-body>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   x-shopify-webhook-id: ...
   x-shopify-api-version: 2024-01

   {"id": 123, "title": "..."}
   ```
2. Using `ShopifyAPI::Webhooks::Request.new` semantics, the HMAC is computed only from the JSON body: [1](#0-0) 
3. Attacker resends the identical body and `x-shopify-hmac-sha256` value, but with `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, raw_body)` and compares it to the (unchanged, still-valid) supplied HMAC — validation succeeds: [6](#0-5) 
5. The handler is invoked with `shop: request.shop` set to `victim-shop.myshopify.com`: [5](#0-4) 
   The host application now processes attacker-controlled `attacker-shop` data as if it belonged to `victim-shop`.

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
