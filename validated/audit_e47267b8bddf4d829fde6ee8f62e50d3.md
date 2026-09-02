Found the identity binding break: in `Webhooks::Request` / `Webhooks::Registry.process`, the HMAC signature is computed only over the raw request body (`to_signable_string` returns `@raw_body`), while the `shop` value that is subsequently trusted and dispatched to the handler comes entirely from the unauthenticated `X-Shopify-Shop-Domain` header, which is never covered by the signature.

### Title
Webhook shop identity spoofing via unauthenticated `X-Shopify-Shop-Domain` header not covered by HMAC - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#shop` reads the merchant's shop domain straight from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, but the HMAC signature validated by `Utils::HmacValidator.validate` is computed only over the raw body (`to_signable_string` returns `@raw_body`) using `HMAC-SHA256(client_secret, raw_body)`. The header is never included in the signed bytes, so the tenant identity `shop` used by the host application is not the field the cryptographic proof actually authenticates.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery`: [1](#0-0) 

`hmac` is derived from the `hmac-sha256` header and `to_signable_string` returns only `@raw_body`. Meanwhile `shop` (line 21-23) is derived independently from the `shop-domain` header, which is disjoint data from what is signed. `Utils::HmacValidator.validate` confirms only that `raw_body` matches the signature computed with `Context.api_secret_key` — it says nothing about which header values accompanied that body: [2](#0-1) 

`Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` and, once it passes, immediately trusts `request.shop` (from the header) to build `WebhookMetadata` and dispatches it to the app's handler as the tenant/shop for that event: [3](#0-2) 

The equality that should hold is: `shop authenticated by HMAC == shop acted upon by the handler`. Here the HMAC only authenticates the byte-identity of `raw_body` (i.e., that *some* payload came from Shopify with a valid secret), while `shop` is taken from a header that is not part of that signed byte stream. Since Shopify's HMAC for webhooks is computed by Shopify over the body only (this matches Shopify's real behavior too — this is not a bug unique to this gem, Shopify webhooks are only signed over body by design), the header value is inherently attacker-controllable data *whenever the raw body's HMAC is otherwise valid for a different, related delivery* — e.g. an app that receives genuine webhook deliveries for shop A can replay the exact same signed raw body while retagging the `X-Shopify-Shop-Domain` header to shop B's domain, and `HmacValidator.validate` will still return `true` because it never inspects headers at all.

### Impact Explanation
If the host application relies on `WebhookMetadata#shop` (populated straight from `request.shop`) as the tenant key to look up sessions, access tokens, or scope database writes, an attacker who can capture (or is themselves the recipient of, e.g. via a legitimately installed low-privilege test/dev shop) one valid signed webhook body can resend it with an arbitrary `X-Shopify-Shop-Domain` value to the app's public webhook endpoint. Because the gem's `HmacValidator` never binds the header to the signature, the forged request passes validation and the host app processes the payload attributed to a shop the attacker does not control — a cross-tenant data/action confusion. This matches the report's "shop authenticated versus shop trusted downstream" identity-binding break class.

### Likelihood Explanation
Exploitability requires the attacker to possess at least one previously-delivered, validly signed webhook body (obtainable from their own installed shop, a public test/dev store, or an intercepted delivery) and network access to the app's public webhook receiver endpoint — both are unprivileged-internet-user capabilities with no `api_secret_key` or access-token compromise needed. The library itself provides no mechanism (nor does it document one) to bind headers to the signature, so any host application that uses `request.shop` or `WebhookMetadata.shop` post-`process` for tenant identification inherits this gap.

### Recommendation
Extend `Utils::VerifiableQuery#to_signable_string` for `Webhooks::Request` (or add an explicit post-validation check in `Registry.process`) to also verify that `shop`, `topic`, and `webhook_id` headers match values embedded in `parsed_body` where Shopify includes them, or otherwise document loudly that `request.shop`/`WebhookMetadata.shop` is unauthenticated header data and must not be used as the sole tenant key without cross-checking it against a shop identifier that is embedded in the signed body/payload itself.

### Proof of Concept
1. App installed on `shop-a.myshopify.com` receives a legitimate webhook: body `B`, header `X-Shopify-Hmac-Sha256: H`, header `X-Shopify-Shop-Domain: shop-a.myshopify.com`. `H = HMAC-SHA256(client_secret, B)`.
2. Attacker (who controls delivery to the endpoint, e.g. by replaying a captured request or being the shop owner of `shop-a`) sends a new HTTP request to the app's webhook endpoint with the same body `B`, same header `X-Shopify-Hmac-Sha256: H`, but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(client_secret, B)` and compares to `H` — this succeeds because the header change never entered the signed bytes: [4](#0-3) [5](#0-4) 
4. `WebhookMetadata` is built with `shop: request.shop` = `"victim-shop.myshopify.com"` and handed to the app's registered handler as an authenticated event for that shop: [6](#0-5) 
5. Any app logic keyed off `WebhookMetadata#shop` (e.g., "delete data for this shop", "update billing state for this shop") now executes against `victim-shop`, a tenant the attacker never authenticated as.

### Citations

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
