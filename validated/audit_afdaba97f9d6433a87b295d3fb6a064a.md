### Title
Webhook `shop` identity is trusted from an HTTP header that is not covered by the HMAC signature, allowing cross-tenant webhook replay - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authorizes a webhook purely by validating the HMAC of the raw request body, then dispatches to the host app's handler using a `shop` value that is read straight from the `X-Shopify-Shop-Domain` header — a field that is never included in the signed bytes. This breaks the identity binding `HMAC-verified bytes == bytes acted upon`: the signature only binds the JSON body to the app's secret, while the tenant identity (`shop`) that the handler uses to decide *which merchant's* state to mutate is unauthenticated.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Utils::HmacValidator.validate` computes/compares the HMAC solely over that signable string [2](#0-1) . Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are all parsed directly from HTTP headers with no cryptographic binding to the signed body [3](#0-2) .

`Registry.process` then checks only the HMAC, and forwards the unauthenticated `request.shop` value straight into the handler as the tenant identifier: [4](#0-3) 

`WebhookMetadata.shop` is a plain `String` field with no relationship to the HMAC-verified payload [5](#0-4) .

The identity binding that should hold is:
`shop authenticated by HMAC == shop acted upon by handler.handle`

Because the HMAC secret (`Context.api_secret_key`) is shared across all shops/tenants of the app (it is the app's secret, not a per-shop secret) [6](#0-5) , any body+HMAC pair that is valid for one shop is *also* a valid HMAC for the same body delivered under a different `shop` header — the signature carries no shop-scoping.

### Impact Explanation
An unprivileged internet user can freely install the target app on their own (attacker-controlled) development/test shop — this requires no access to `api_secret_key`, access tokens, or any privileged account. Doing so, Shopify will deliver genuinely-signed webhooks (e.g. `app/uninstalled`, `shop/redact`, etc.) to the app's public webhook endpoint, giving the attacker a valid `(raw_body, hmac)` pair signed with the app's real secret. The attacker can then replay that exact body and HMAC to the same public endpoint while substituting an arbitrary victim `X-Shopify-Shop-Domain` header. `HmacValidator.validate` still succeeds (it only checks body bytes), so `Registry.process` invokes the host handler with `WebhookMetadata.shop` set to the victim shop. Any host application logic that uses `data.shop` to select/mutate per-tenant state (e.g., deleting a stored session/access token on `app/uninstalled`, or looking up and processing a shop's data on GDPR topics) can be forced to act on a shop the attacker does not control — a cross-tenant identity-confusion issue that crosses the tenant boundary the HMAC was meant to enforce.

### Likelihood Explanation
Reachability is high: the webhook endpoint is by design public and unauthenticated aside from the HMAC check; obtaining a valid signed body requires only installing the app on any shop, which is a routine, unprivileged action available to any Shopify Partner/developer account. No leaked credentials, TLS interception, or social engineering are needed.

### Recommendation
Bind the shop identity to the signed payload before it reaches the handler:
- Include the shop domain (and ideally topic) inside the signable string used for HMAC verification, or
- After HMAC validation, independently verify that `request.shop` corresponds to a shop the host app actually has an active session for (this is partially a host-app responsibility, but the gem should document/enforce that `shop` is unauthenticated header data and must not be used as a trust anchor without additional verification), and
- Consider deriving `shop` from a value that is itself part of the signed body where the webhook payload includes it, rather than exclusively from the header.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`, triggering a real `app/uninstalled` webhook signed by Shopify with the app's `client_secret`.
2. Attacker captures the raw POST body and the `X-Shopify-Hmac-Sha256` header from that legitimate delivery.
3. Attacker sends a new POST request directly to the app's public webhook endpoint with the identical raw body/HMAC, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` returns `true` (body bytes unchanged), `Registry.process` builds `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "app/uninstalled", ...)` [4](#0-3)  and invokes the host's registered handler, which typically deletes/invalidates the session stored for `victim-shop.myshopify.com`, despite the attacker having no relationship to that shop.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
