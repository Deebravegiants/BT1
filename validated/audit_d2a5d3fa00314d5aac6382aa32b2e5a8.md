### Title
Webhook `shop-domain` header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw body alone, while the `shop`, `topic`, `webhook_id`, and `api_version` values consumed downstream come from unauthenticated HTTP headers. Because `Registry.process` trusts `request.shop` as the tenant identifier for dispatching the webhook without that value being part of the HMAC-protected data, any party in possession of a single genuine `(raw_body, hmac)` pair (e.g., a merchant who installed the app on their own store and received one legitimate webhook) can replay the same body/HMAC combination while swapping the `shop-domain` header to a different tenant, causing the host application to process the webhook as if it originated from that other shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` only checks that `verifiable_query.hmac` matches `HMAC(secret, to_signable_string)`, i.e., `HMAC(secret, raw_body)` for webhook requests: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identity for dispatch, passing it into `WebhookMetadata` for the handler without any additional binding to the signed content: [4](#0-3) 

The equality the gem is implicitly relying on is:
`shop used for tenant dispatch (request.shop, header-derived)` == `shop that produced the HMAC (implicit in raw_body, but not actually bound to it)`

This equality does not hold: the `shop-domain` header can be freely changed after a valid `(body, hmac)` pair is obtained, and the HMAC check will still pass because the header is not part of the signed data.

### Impact Explanation
This breaks the tenant boundary the gem's webhook processing depends on. An unprivileged internet user who runs the app on their own Shopify store (a normal, unprivileged merchant-level capability) legitimately receives real webhooks with valid `(raw_body, hmac)` pairs for their own shop. By capturing one such delivery and re-sending it to the app's webhook endpoint with the `x-shopify-shop-domain`/`shopify-shop-domain` header rewritten to a victim shop's domain, the request still passes `HmacValidator.validate` (since only the body is checked), and `Registry.process` will hand the handler a `WebhookMetadata` claiming to be from the victim shop. Any host application that uses `request.shop` from this gem to look up store-specific data, apply per-shop state changes, or trigger tenant-scoped side effects (data deletion, GDPR redact handlers such as `shop/redact`/`customers/redact`, order/inventory updates, etc.) will act on the wrong tenant, resulting in cross-tenant access/manipulation.

### Likelihood Explanation
Likelihood is Medium/High: any user who can install the app on a shop they control gets an inexhaustible supply of validly-HMAC'd bodies (webhooks fire routinely, and can often be triggered by ordinary store actions like updating a product or creating an order). Forging the header swap requires no cryptographic secret at all — only a way to submit an HTTP POST with attacker-controlled headers to the app's public webhook endpoint, which is by design internet-reachable.

### Recommendation
Bind the tenant-identifying fields to the signature verification instead of trusting header values independently of the HMAC:
- Prefer deriving/validating the shop by cross-checking it against a shop that's independently known to be the intended recipient (e.g., via the URL path/route tied to the specific shop's session, or via looking up the registered webhook by `webhook_id` and cross-verifying its expected shop) rather than trusting the raw header.
- At minimum, document prominently that `request.shop`, `request.topic`, and `request.webhook_id` are NOT authenticated by the HMAC check and must not be used by host applications as the sole tenant/authorization key without additional verification (e.g., confirming the shop is one that has an active, valid session/installation record before acting on the payload).

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook delivery:
   - Headers: `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - Body: `{"id": 123, ...}`
2. Attacker resends the exact same body and `hmac-sha256` header to the app's webhook endpoint, but changes only:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only re-hashes `request.to_signable_string` (i.e. the untouched raw body) — validation succeeds: [5](#0-4) 
4. The handler receives `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: ..., ...)` and the host application processes it as authentic data for `victim-shop`, even though the payload never originated from Shopify for that shop.

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
