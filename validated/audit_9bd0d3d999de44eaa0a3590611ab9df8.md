### Title
Webhook `shop-domain`/`topic` headers are trusted for tenant identity without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes/exposes the HMAC only over the raw request body, while the `shop`, `topic`, `api_version`, and `webhook_id` values are read straight from unauthenticated HTTP headers and then handed to the app's webhook handler as trusted tenant/routing metadata.

### Finding Description
`Registry.process` accepts a request as authentic solely based on `Utils::HmacValidator.validate(request)` succeeding: [1](#0-0) 

`HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only the raw body (`@raw_body`), and `hmac` is decoded solely from the `hmac-sha256` header: [3](#0-2) [4](#0-3) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are read directly from headers with no cryptographic binding to the signed body at all: [5](#0-4) 

Once `HmacValidator.validate` passes, `Registry.process` dispatches to the handler with `shop: request.shop` taken verbatim from the header, used as the tenant identifier for the delivered event: [6](#0-5) 

The identity binding the app relies on is effectively:
`HMAC-verified(body) == body used by handler` AND (implicitly, but not actually enforced) `shop header == shop that produced this HMAC-signed body`.

Because `shop-domain` (and `topic`/`webhook-id`) are outside the signed payload, any request with a body+HMAC pair that validates (e.g., one captured from a genuine webhook delivered to the attacker's own shop, or any body an attacker can get validly signed for) can be replayed to the same endpoint with an arbitrary `x-shopify-shop-domain` header substituted. `HmacValidator.validate` still returns `true` because it never inspects the shop header, and `Registry.process` will hand the handler a `WebhookMetadata` claiming to be from the attacker-chosen shop, while the actual signed content originated from a different shop.

### Impact Explanation
This breaks the equality `shop authenticated by HMAC == shop stored/acted upon by the handler`, which is exactly the kind of tenant-identity-binding failure called out as in-scope (analogous to the ECDSA signature-malleability class: a signature that validates the wrong logical message). If an app uses `WebhookMetadata#shop` to select which merchant's stored data/session to update (the intended, documented usage pattern for webhook handlers), an unprivileged attacker who can obtain any one validly-HMAC'd body (for instance by installing the app on a shop they control and receiving genuine webhook deliveries) can relabel that request as coming from an arbitrary other shop domain and have the handler act on/against that victim tenant's context — a cross-tenant confusion at the delivery layer.

### Likelihood Explanation
Exploitability requires only capturing one valid `(body, hmac)` pair — obtainable without any secret, privileged account, or credential leak, e.g. by installing the app to any shop and observing a real webhook delivery to the app's own public endpoint — then replaying it with a modified `shop-domain`/`topic` header. No `api_secret_key` or access token is needed. The only mitigating factor is that the resulting impact depends on how much the host application trusts `data.shop`/`data.topic` without additional server-side correlation (e.g., matching against a stored session for that shop), which is outside this gem's control but is exactly the binding this gem hands to the app as "verified."

### Recommendation
Include the identity-critical headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable payload used for HMAC verification, or otherwise cryptographically bind them to the verified body (e.g., verify against a Shopify-provided event ID/nonce store, or require the app to cross-check `shop` against an already-established session before trusting `WebhookMetadata#shop`). At minimum, update `VerifiableQuery#to_signable_string` for `Webhooks::Request` so `HmacValidator` cannot pass for a body whose accompanying identity headers have been swapped.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and lets Shopify deliver a real webhook (e.g., `orders/create`) to the app's public webhook endpoint. Attacker records the full raw body and the `x-shopify-hmac-sha256` value — both valid and HMAC-signed by Shopify with the app's real secret.
2. Attacker resends the exact same body and HMAC header to the same endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `x-shopify-topic`/`x-shopify-webhook-id`).
3. `ShopifyAPI::Webhooks::Request#hmac`/`#to_signable_string` only look at the body and `hmac-sha256` header, so `HmacValidator.validate` returns `true` ( [3](#0-2) , [7](#0-6) ).
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)` ( [1](#0-0) ), even though the signed body never originated from that shop — demonstrating the handler receives an unauthenticated tenant identity alongside an authenticated body.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-22)
```ruby
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

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
