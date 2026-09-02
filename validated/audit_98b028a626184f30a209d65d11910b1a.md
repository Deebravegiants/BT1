## Title
Webhook `shop-domain` (and `topic`/`webhook-id`/`api-version`) header is trusted by the handler but not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while `Registry.process` trusts the `shop-domain` header (and `topic`, `webhook_id`, `api_version`) as authoritative tenant-identifying metadata when dispatching to the app's webhook handler. Because these headers are never included in the signed material, an attacker who can obtain any single valid `(raw_body, hmac)` pair for the app (e.g., by installing the app on their own store and capturing a webhook it receives) can replay that exact body/HMAC pair while substituting the `X-Shopify-Shop-Domain` header for a victim shop. The signature still validates, and the host app's handler executes attacker-controlled webhook data attributed to the victim's tenant.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` verifies a `VerifiableQuery` by recomputing an HMAC-SHA256 over `verifiable_query.to_signable_string` using `Context.api_secret_key`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw HTTP body — none of the Shopify-supplied headers are included: [2](#0-1) 

`Registry.process` validates the HMAC and then unconditionally trusts `request.shop` (parsed straight from the `shop-domain`/`x-shopify-shop-domain` header) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The equality the code implicitly assumes is:

`shop that authorized/produced this HMAC == shop attributed in WebhookMetadata (request.shop)`

But since `shop-domain` is not part of the signed bytes, this equality does not hold: the HMAC only proves "this body was signed by our app's client secret at some point, for some shop," not "this body came from `request.shop`." Because the app's `client_secret` (and thus HMAC key) is shared across every shop that installs the app, any tenant that can trigger a legitimate webhook for itself possesses a valid `(body, hmac)` pair that remains valid for any header combination.

### Impact Explanation
This breaks the tenant-identity binding between the cryptographic proof (HMAC over body) and the tenant-identifying data (`shop`) that host applications rely on to route/attribute webhook data (e.g., write to a specific shop's records, trigger data sync, revoke resources, etc.). An attacker with a legitimately installed instance of the target app on their own shop can force the app to process attacker-controlled body content while asserting it belongs to a victim shop, achieving cross-tenant data injection/confusion — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only capabilities available to any unprivileged internet user who installs the target Shopify app on a store they control (a standard workflow, not a privileged action, and does not require the app's `client_secret` or a merchant's access token). The attacker captures one authentic `(raw_body, hmac)` webhook pair from their own installation, then replays it to the app's public webhook endpoint with an altered `shop-domain` header. No secret material needs to be recovered because the signed bytes never depended on it.

### Recommendation
Bind the tenant/topic identity into the signed material, or otherwise cryptographically tie the `shop-domain`, `topic`, and `webhook-id` headers to the signature verification — e.g., include them in `to_signable_string`, or require the host application to cross-check `request.shop` against a shop that is independently known to have an active, previously-established relationship for that specific webhook subscription (e.g., matching a per-shop webhook ID stored at registration time) rather than trusting the header value on its own.

### Proof of Concept
1. Attacker creates a Shopify store and installs the vulnerable app (standard OAuth flow, no special access).
2. Shopify sends the attacker's app a webhook, e.g. `orders/create`, with body `B` and header `X-Shopify-Hmac-Sha256: H` (a valid HMAC of `B` using the app's shared `client_secret`).
3. Attacker resends the exact same body `B` and `hmac-sha256` header `H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC solely over `@raw_body` (`B`) and succeeds, since the header is not part of `to_signable_string`.
5. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)` and processes attacker-controlled data as if it originated from the victim's store.

### Citations

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
