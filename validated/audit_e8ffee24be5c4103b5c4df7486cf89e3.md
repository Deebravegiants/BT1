Confirmed root cause. Writing up the finding.

### Title
Webhook shop/topic identity spoofing via HMAC that only covers the raw body, not the `shop-domain`/`topic` headers - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the tenant-identifying fields `shop`, `topic`, `api_version`, and `webhook_id` are read directly from unauthenticated HTTP headers. `Registry.process` validates the HMAC against the body alone and then dispatches the handler using the header-derived `shop`, so the value the handler trusts as the tenant is never covered by the signature it just verified.

### Finding Description
`Registry.process` gates webhook handling on `Utils::HmacValidator.validate(request)`: [1](#0-0) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns `@raw_body` exclusively - the `shop`, `topic`, `api_version`, and `webhook_id` accessors are all pulled straight from the (attacker-controlled) HTTP headers and are not part of the signed material: [3](#0-2) 

The equality the code implicitly relies on is:
`HMAC_valid(body, secret) == true` implies `shop_header == origin_shop`

but the actual guarantee provided is only:
`HMAC_valid(body, secret) == true` implies `body` was signed by the app's secret for *some* shop event — it says nothing about which `shop-domain` header accompanies that body.

Because the webhook endpoint is a public HTTP endpoint (that's the point of webhooks), any unprivileged internet user who has ever received one legitimate webhook delivery for their own store (i.e., any merchant who installs the app) possesses a valid `(raw_body, hmac)` pair. That pair remains valid under `HmacValidator.validate` regardless of which `x-shopify-shop-domain` / `x-shopify-topic` / `x-shopify-webhook-id` header values are sent alongside it, since those headers are excluded from the signed string. The attacker can therefore resend the same body/HMAC to the app's webhook endpoint with a forged `shop-domain` header naming a different (victim) shop, and the gem will pass it straight to the registered handler as `WebhookMetadata.new(topic:, shop: request.shop, ...)`, attributing the event to the wrong tenant.

### Impact Explanation
This breaks the tenant-isolation boundary the HMAC check is supposed to enforce: an app relying on `request.shop` (as returned by this gem) to select which merchant's session/data to act on can be made to process an attacker-supplied, validly-signed payload under a different shop's identity — a cross-tenant confusion/spoofing primitive reachable by any user who can install the app on any shop (including their own) and capture one webhook delivery. Depending on how the host app uses the `shop` value from `WebhookMetadata` (e.g., to look up the merchant's session/access token or to write data under that shop's record), this can escalate to cross-tenant data corruption or a foothold for further attacks against a shop the attacker does not control.

### Likelihood Explanation
Any Shopify merchant is, by definition, an unprivileged actor with respect to a third-party app. Once they install the app they receive real webhook deliveries with a valid `(body, hmac)` pair for their own store, which costs nothing to capture. Replaying that pair with a different `shop-domain` header requires no secret, no privileged access, and no network position beyond being able to POST to the app's public webhook URL. The likelihood of exploitation is limited only by whether the specific webhook `topic`/body content is meaningful/actionable when misattributed to another shop, which is host-application-dependent but plausible for many topics (e.g., topics whose bodies do not embed the shop's own domain).

### Recommendation
Bind the identifying headers into the signed material that `HmacValidator` checks — e.g., include `shop-domain`, `topic`, and `webhook_id` in `Webhooks::Request#to_signable_string` (or otherwise cryptographically bind them to the body) so that `HmacValidator.validate` fails if any of these header values are altered relative to what Shopify actually sent. At minimum, document clearly that `request.shop`/`request.topic` are unauthenticated header values and that host applications must not treat a passing `HmacValidator.validate` result as vouching for them.

### Proof of Concept
1. Install the app on shop `attacker.myshopify.com` (or use any account entitled to receive webhooks) and capture one legitimate webhook delivery: raw body `B` and header `x-shopify-hmac-sha256: H` (valid for `B` under the app's secret).
2. Send a new HTTP POST to the app's webhook endpoint with the same body `B` and the same header `H`, but replace the headers `x-shopify-shop-domain` with `victim-shop.myshopify.com` and (optionally) `x-shopify-webhook-id`/`x-shopify-topic` with arbitrary values.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` is constructed; `Utils::HmacValidator.validate(request)` returns `true` because it only checks `B` against `H`.
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(topic: forged_topic, shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, i.e., the host application's handler executes believing this event legitimately originated from `victim-shop.myshopify.com`.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```
