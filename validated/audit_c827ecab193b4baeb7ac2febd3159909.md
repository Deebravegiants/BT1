### Title
Webhook Cross-Tenant Data Injection via Shop Header Not Covered by HMAC Signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` and `ShopifyAPI::Utils::HmacValidator` authenticate an incoming webhook by validating the HMAC-SHA256 signature of the **raw request body only**. The `shop` domain (and `topic`/`api_version`/`webhook_id`) are read from HTTP headers that are **not part of the signed content**, so the signature never binds a given payload to the shop it claims to originate from.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `#shop` is derived purely from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, entirely outside the signed data: [2](#0-1) 

`Utils::HmacValidator.validate` computes the expected signature strictly over `verifiable_query.to_signable_string` (i.e., the raw body) and compares it to the `hmac` field taken from the `hmac-sha256` header: [3](#0-2) 

`Webhooks::Registry.process` relies on this validation, then trusts `request.shop` (and `request.topic`) as authenticated tenant context for the handler: [4](#0-3) 

The identity binding broken here is: `shop header used by handler == shop bound by HMAC signature`. In reality, the signature only proves `body == body signed with client_secret`; it says nothing about which shop that body belongs to. An unprivileged internet user who legitimately owns/operates any Shopify store receives real webhooks from Shopify with a valid `(raw_body, hmac)` pair for their own store. Because `shop-domain` is excluded from the signed content, that same `(raw_body, hmac)` pair remains cryptographically valid when replayed to the app's public webhook endpoint with the `shop-domain` header rewritten to point at a victim shop. `HmacValidator.validate` will pass, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the (attacker-controlled) body originates from the victim shop.

### Impact Explanation
This crosses a tenant boundary: an attacker can cause an app to process arbitrary (but validly-signed-for-some-shop) webhook payloads as if they belong to a different, victim merchant's shop. Depending on how the host application's webhook handler uses `shop` (e.g., updating shop-scoped records, triggering shop-specific side effects, writing audit/billing data), this enables cross-tenant data injection/corruption without needing any credentials belonging to the victim. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is realistic for anyone who can obtain at least one legitimately-signed webhook body/HMAC pair (trivial for an attacker who has any live shop installed with the target app, since Shopify sends them real signed webhooks routinely) and can send an HTTP POST directly to the app's public webhook endpoint (which is inherently internet-reachable, that being the entire point of webhooks). No access token, `client_secret`, or privileged account is required — only a body+HMAC pair the attacker already legitimately possesses and header manipulation on their own outbound request.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the signed content bound by the HMAC, or otherwise cryptographically bind the shop-domain header to the signature (e.g., verify the header-derived shop against a per-shop stored secret/session rather than trusting it as authenticated solely because the body-only HMAC passed). At minimum, document clearly that `request.shop` is unauthenticated header data and must not be trusted as tenant identity without additional verification (e.g., cross-checking against an already-known installed shop list before acting on shop-scoped data).

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and receives a legitimate webhook POST from Shopify, e.g.:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid-hmac-for-body>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   x-shopify-webhook-id: ...
   Body: {"id":1,...attacker-controlled order data...}
   ```
2. Attacker captures the raw body and the accompanying `x-shopify-hmac-sha256` value (both are visible/interceptable on their own request).
3. Attacker replays the exact same body and HMAC header to the app's public webhook endpoint, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the signature over the raw body only, matches the replayed HMAC, and returns `true`.
5. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` invokes the handler with `shop: "victim-shop.myshopify.com"` and the attacker-supplied body, even though the data never actually came from Shopify on behalf of that shop.

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
