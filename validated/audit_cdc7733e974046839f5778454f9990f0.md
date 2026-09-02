### Title
Webhook shop-domain, topic, webhook-id and api-version are not covered by the HMAC, allowing a valid webhook to be replayed with a spoofed tenant identity - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate`/`validate_signature` compute and compare the HMAC solely over that signable string [2](#0-1) . Meanwhile `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read directly from HTTP headers, none of which participate in the HMAC computation [3](#0-2) . `Registry.process` validates only the body HMAC and then forwards the unauthenticated `shop`, `topic`, and `webhook_id` header values straight into the handler via `WebhookMetadata` [4](#0-3) .

### Finding Description
The binding that should hold is: `hmac == HMAC(secret, shop ∥ topic ∥ webhook_id ∥ body)`, i.e. the identity fields the app acts on (especially `shop`) should be cryptographically bound to the signature. Instead the actual binding implemented is `hmac == HMAC(secret, body)` only [5](#0-4) .

Because `shop-domain`, `topic`, `webhook-id`, and `api-version` are ordinary headers taken verbatim with no cryptographic tie to the signed body [6](#0-5) , any party capable of observing one legitimate (body, hmac) pair sent by Shopify for shop A can resend that same body and hmac to the app's webhook endpoint while substituting a different `x-shopify-shop-domain` (and/or `topic`/`webhook-id`) header value. `HmacValidator.validate` will still succeed because it only recomputes/compares the HMAC against the body [7](#0-6) , yet `Registry.process` will pass the attacker-controlled `shop` value into `WebhookMetadata` and the app's `handler.handle` [8](#0-7) . Any host application that keys per-tenant state, session lookup, or data writes off `data.shop` (as intended, since `WebhookMetadata#shop` is the const documented for that purpose [9](#0-8) ) will process the payload under the wrong tenant's identity, i.e. the "shop authenticated" (the header value forwarded to the handler) diverges from "the shop that actually produced the signed body."

### Impact Explanation
This breaks the tenant-authentication boundary of an incoming webhook: an unprivileged actor with visibility into any single legitimate webhook delivery (e.g., a request/response logging proxy, replayed traffic, or a webhook forwarding service) can cause the gem to attribute a validly-signed payload to an arbitrary `shop` value of the attacker's choosing, without knowing the app's `client_secret`. Downstream, this is a cross-tenant identity-confusion primitive: any handler relying on `WebhookMetadata#shop` for tenant scoping (session lookup, DB row selection, webhook-id deduplication) can be made to act on shop B's data using shop A's signed body. This matches the "Critical - cross-tenant access" impact class since the HMAC is meant to authenticate the whole webhook delivery, not merely the JSON body.

### Likelihood Explanation
Exploitation requires capturing one legitimate (body, hmac) pair for any shop that uses the app — feasible via network observation, logging, request replay, or a malicious webhook-forwarding proxy, none of which require the app's `client_secret` or an access token. The header substitution itself is trivial (a normal unauthenticated HTTP request to the app's public webhook endpoint). This keeps the finding within scope (no privileged credential required) while requiring a realistic MITM/replay opportunity, so likelihood is moderate rather than trivial.

### Recommendation
Bind the tenant/topic identity into the signed material actually verified, or independently re-derive/verify `shop`, `topic`, and `webhook_id` against a source not solely controlled by request headers before use. Concretely: extend `to_signable_string` (or add an additional check in `HmacValidator`/`Registry.process`) to incorporate `shop`, `topic`, and `webhook_id` into the HMAC computation, matching what Shopify actually signs, or reject/re-verify shop domain format against the session store the token was issued for rather than trusting the header value used for handler dispatch.

### Proof of Concept
1. Attacker observes (via a proxy, logs, or network capture) one legitimate webhook delivery to the app: headers `x-shopify-shop-domain: shopA.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, and body `B`.
2. Attacker sends a new POST to the app's webhook endpoint with the same body `B` and same `x-shopify-hmac-sha256`, but `x-shopify-shop-domain: shopB.myshopify.com`.
3. `Request#hmac` and `Request#to_signable_string` return the same values as before (hmac header and `@raw_body`) [10](#0-9) ; `HmacValidator.validate` recomputes HMAC over `B` only and it matches [7](#0-6) .
4. `Registry.process` proceeds and calls `handler.handle` with `WebhookMetadata.new(... shop: request.shop ...)`, where `request.shop` is now `"shopB.myshopify.com"` [8](#0-7) , even though the signed payload actually originated from shop A.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L11-13)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-21)
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
