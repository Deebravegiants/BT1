### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook forgery via HMAC replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the HMAC signature over the raw request body only, while the `shop` (tenant identity) is read from an unauthenticated header and passed straight through to the application's webhook handler as verified data. This breaks the equality `shop used to route/process the webhook == shop actually authenticated by the HMAC`.

### Finding Description
`Request#to_signable_string` returns only the raw body, never the `shop-domain` header: [1](#0-0) 

`Request#shop` is read directly, unauthenticated, from a header: [2](#0-1) 

`Utils::HmacValidator.validate` computes and compares the signature exclusively over `verifiable_query.to_signable_string` (i.e., the body): [3](#0-2) 

`Registry.process` accepts any request whose body-HMAC validates, and then forwards `request.shop` — the unauthenticated header — as the tenant identity to the handler, with no additional binding check tying it to the signed bytes: [4](#0-3) 

Because the signature only binds the request body, and never the shop header, the two identities the gem treats as equivalent — "the shop whose data was HMAC-authenticated" and "the shop attributed to the resulting `WebhookMetadata`" — are not actually the same value. An attacker who can obtain any single valid `(body, hmac)` pair (e.g., because they run their own Shopify store and receive legitimate webhooks addressed to their own tenant, which is an unprivileged, self-serve action) can resend that exact body and HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop. `HmacValidator.validate` will still succeed because it never inspects the shop header, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the (attacker-controlled) payload originated from the victim shop.

### Impact Explanation
This crosses a tenant boundary: an attacker who is an unprivileged internet user (or unprivileged merchant, since they only need to receive one webhook delivery to their own store) can inject forged webhook events that the host application will process as belonging to another merchant's shop. Any app logic keyed off `WebhookMetadata#shop` (e.g., updating per-shop records, entitlements, billing, or triggering per-shop side effects) can be manipulated cross-tenant. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only: (1) the attacker possesses at least one legitimately delivered webhook body+HMAC pair from Shopify — trivial to obtain by installing the target app on the attacker's own store and waiting for any webhook — and (2) the ability to send an HTTP request to the app's public webhook endpoint with a spoofed shop header, which is standard unprivileged HTTP access. No secrets, tokens, or privileged access are required, making this readily reachable.

### Recommendation
Bind the shop identity into the verified signable content, or otherwise cryptographically tie the shop header to the signed payload before trusting it. At minimum, `Registry.process` (or `Request`) should cross-check `request.shop` against an application-supplied allow-list/expected value derived from an authenticated source (e.g., the shop associated with the webhook subscription being looked up), rather than passing the raw unauthenticated header straight into `WebhookMetadata`.

### Proof of Concept
1. Install the target app on attacker-controlled store `attacker.myshopify.com`; capture a legitimate webhook delivery — raw body `B` and its valid `X-Shopify-Hmac-Sha256` header `H` (computed by Shopify over `B` with the app's secret).
2. Replay the request to the app's webhook endpoint, keeping body `B` and header `H` unchanged, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` in [5](#0-4)  succeeds, since it only recomputes HMAC over `B`.
4. `Registry.process` in [4](#0-3)  invokes the app's handler with `shop: "victim.myshopify.com"` and the attacker-controlled body `B`, even though `B` was never signed for `victim.myshopify.com`.

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
