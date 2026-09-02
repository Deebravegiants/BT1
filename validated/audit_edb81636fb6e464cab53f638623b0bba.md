### Title
Webhook shop/topic/id attribution is not covered by the HMAC signature, allowing cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` from unauthenticated HTTP headers, while `to_signable_string` — the value actually covered by the HMAC check in `Utils::HmacValidator.validate` — is only the raw request body. `Registry.process` trusts `request.shop` as the authoritative tenant identifier and hands it straight to the app's webhook handler. This breaks the identity binding `shop authenticated by HMAC == shop attributed to the webhook`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all read from HTTP headers, independent of the signed payload: [2](#0-1) 

`Utils::HmacValidator.validate` verifies `verifiable_query.hmac` against `verifiable_query.to_signable_string` only: [3](#0-2) [4](#0-3) 

`Registry.process` performs this HMAC check and then trusts `request.shop`/`request.topic`/`request.webhook_id` verbatim, forwarding them into `WebhookMetadata` passed to the app's handler: [5](#0-4) 

Since the HMAC digest is computed only over the raw body (using the app's single, shop-independent `client_secret`), it is identical for the same body regardless of which shop header accompanies the request. An attacker who legitimately installs the app on their own store will receive real, correctly-signed webhooks from Shopify (valid `raw_body` + valid `hmac`). They can capture that pair and replay it directly to the app's public webhook endpoint with the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header swapped to reference a different, victim shop. `HmacValidator.validate` still passes because it only checks the body, not the header the app uses to decide "which tenant does this event belong to."

The equality that should hold but doesn't:
`shop covered by HMAC == shop used to route/act on the webhook`
Before the attacker's request: signed body corresponds to (attacker shop, attacker body). After the crafted replay: the app processes (victim shop, attacker-controlled body) as if Shopify itself asserted this pairing — but nothing in the signed material ties the shop header to the body.

### Impact Explanation
This is a cross-tenant boundary violation: an unprivileged actor who installs the app once (a normal, non-privileged action available to anyone) can then forge webhook deliveries attributed to any other shop domain, including the mandatory compliance topics (`shop/redact`, `customers/redact`, `customers/data_request`) and any registered business-data topics (`orders/create`, `app/uninstalled`, etc.). Any host application relying on `WebhookMetadata#shop` to select/update per-tenant records (which is exactly the field's documented purpose) can be tricked into applying attacker-supplied bodies to a different merchant's tenant, or into triggering redaction/uninstall-style side effects for a shop that never sent that event. This matches the Critical/High impact bar of cross-tenant access through the library's own trust boundary (the HMAC check that is supposed to authenticate the webhook).

### Likelihood Explanation
Likelihood is moderate-to-high for any app that lets outside merchants self-install (the typical distribution model): obtaining one genuine signed webhook only requires installing the app and triggering any subscribed event on your own store; no access to `api_secret_key` or another merchant's credentials is needed. The only work required is replaying the captured request with a modified shop/topic header via a normal HTTP client, since the library's `HmacValidator` never inspects those headers.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` (or at minimum `shop`) inside the value returned by `to_signable_string`/covered by the HMAC check, or independently validate that the shop asserted in the header corresponds to a shop with an active session/installation known to the app before dispatching to handlers. At minimum, document that `request.shop` is not authenticated by the HMAC and must not be trusted for tenant routing without additional verification.

### Proof of Concept
1. Install the app on attacker-owned shop `attacker.myshopify.com`; trigger a subscribed topic (e.g., `orders/create`) so Shopify sends a legitimately signed webhook with body `B` and header `x-shopify-hmac-sha256: H` (computed by Shopify using the app's `client_secret` over `B`).
2. Capture `B` and `H` from the delivered request.
3. Send a new POST directly to the app's webhook endpoint with the same body `B` and same `x-shopify-hmac-sha256: H`, but set `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` accepts the request; `Utils::HmacValidator.validate` passes because it only checks `to_signable_string` (`B`) against `H`, both unchanged. [5](#0-4) 
5. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and the attacker-controlled body `B`, processing it as an authentic event from `victim.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
