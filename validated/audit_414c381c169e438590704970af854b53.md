Confirmed. This gives enough evidence to finalize the finding.

### Title
Webhook shop and topic identifiers are not covered by HMAC verification, allowing tenant identity spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` directly from unauthenticated HTTP headers, while the HMAC signature validated by `Utils::HmacValidator` only covers the raw request body. `Registry.process` trusts these header-derived values and forwards them unchanged to the host application's webhook handler, breaking the binding between "bytes verified by HMAC" and "shop identity acted on."

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `#shop`, `#topic`, `#webhook_id`, and `#api_version` are read straight from the `x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`, and `x-shopify-api-version` headers, none of which are included in the signed payload: [2](#0-1) 

`Utils::HmacValidator.validate` only checks that `to_signable_string` (the raw body) matches the HMAC, using `Context.api_secret_key`: [3](#0-2) 

`Registry.process` then raises only on invalid body HMAC, and immediately trusts `request.shop`/`request.topic` (unauthenticated) to dispatch to the registered handler and build `WebhookMetadata`: [4](#0-3) 

`WebhookMetadata#shop` is a plain `String` field with no further verification, and is the value the host application's `WebhookHandler#handle` implementation is expected to use as the tenant identity for the incoming event: [5](#0-4) 

The identity binding that should hold is: `HMAC-authenticated raw_body` ⇔ `shop that generated it`. Instead, the gem only proves `HMAC-authenticated raw_body` ⇔ `Shopify's secret was used at some point`, while `shop` is taken verbatim from an attacker-controllable header on the incoming HTTP request that this gem parses.

### Impact Explanation
Any actor who can deliver an HTTP POST to the app's webhook endpoint (e.g., a merchant who has legitimately installed the app on their own shop and captured a real, validly-signed webhook body/HMAC pair sent to them by Shopify) can replay that same body/HMAC with the `x-shopify-shop-domain` header changed to an arbitrary victim shop domain. `HmacValidator.validate` will still pass because it never inspects the shop header, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event belongs to the victim shop. If the host application uses `data.shop` (as documented/intended by this gem's API) to key session lookups, database writes, or trigger tenant-scoped side effects (e.g. acting on `app/uninstalled` or `shop/redact` for a victim tenant), this results in cross-tenant data manipulation attributed to a shop the attacker does not control.

### Likelihood Explanation
Exploitation requires only the ability to send HTTP requests to the app's public webhook endpoint plus possession of one genuine, previously-delivered webhook body+HMAC pair for any shop (trivially obtainable by installing the app on an attacker-controlled shop). No access to `client_secret`, access tokens, or Shopify infrastructure is needed, since the vulnerable check is entirely local to this gem's `HmacValidator`/`Request`/`Registry` code path.

### Recommendation
Include the shop domain (and ideally topic) in the HMAC-signed payload used by `to_signable_string`, or otherwise cross-validate `request.shop` against a fact tied to the signature (e.g., require the shop header to match a shop with an active, previously-registered session/webhook subscription before dispatching to the handler) so that a spoofed `x-shopify-shop-domain` header cannot pass validation.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and lets Shopify deliver a real webhook (e.g. `orders/create`) to the app's endpoint, capturing the raw body `B` and its valid header `x-shopify-hmac-sha256: H`.
2. Attacker sends a new POST to the same webhook endpoint with body `B` and `x-shopify-hmac-sha256: H` unchanged, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`= B`) and finds it matches `H`, so validation succeeds: [6](#0-5) 
4. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: JSON.parse(B), ...)`, causing the host application to process attacker-controlled data as if it originated from the victim's shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-28)
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-24)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end

    module WebhookHandler
      include Kernel
      extend T::Sig
      extend T::Helpers
      interface!

      sig do
        abstract.params(data: WebhookMetadata).void
      end
      def handle(data:); end
    end
```
