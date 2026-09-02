## Finding

### Title
Webhook shop-domain header is not covered by HMAC signature, enabling cross-tenant webhook replay - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the webhook's `hmac` signature only over the raw request body, while the `shop` (and `topic`/`webhook_id`) values are read from unauthenticated HTTP headers. `Webhooks::Registry.process` validates only the HMAC-over-body and then hands the header-derived `shop` value to the app's handler as trusted metadata. An entity that can obtain one genuine, HMAC-signed webhook payload (e.g. a merchant receiving webhooks for their own shop) can replay that exact body+HMAC pair while substituting the `X-Shopify-Shop-Domain` header for a different (victim) shop, and the signature will still validate.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, and `#webhook_id` are all parsed straight from HTTP headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`HmacValidator.validate` verifies the signature strictly against `to_signable_string`, i.e. only the raw body bytes: [3](#0-2) 

`Registry.process` performs no additional binding check between the validated body and the header-derived `shop`; it passes `request.shop` straight to the registered handler as authenticated metadata: [4](#0-3) 

The identity binding that should hold is:
`HMAC(body) valid ⇒ shop-domain header == the shop that produced body`

But the actual code only proves `HMAC(body) valid`; the `shop` header is unauthenticated and can be freely substituted without invalidating the signature, breaking that binding.

### Impact Explanation
An attacker who legitimately installs the app on their own shop (or otherwise captures one genuine, correctly-signed webhook body+HMAC pair) can resend that exact payload to the app's webhook endpoint while changing only the `X-Shopify-Shop-Domain` header to name a different shop. Because the HMAC covers only the body, the signature still verifies, and `Registry.process` calls the handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop while `body`/`topic`/`webhook_id` come from the attacker's own webhook. Any host application that trusts `data.shop` from the processed webhook to select which tenant's records to look up, update, or notify (a natural and encouraged use per the library's own webhook docs and `WebhookMetadata` design) will apply attacker-controlled data to the wrong tenant — a cross-tenant data-integrity/confusion issue.

### Likelihood Explanation
Requires the attacker to control (or otherwise obtain) at least one genuine signed webhook, which is realistic for any public app since any merchant who installs it receives legitimately signed webhooks for their own store. No access to `api_secret_key`, access tokens, or any Shopify-side credentials is needed — only header rewriting on replay, which is trivial for any client sending raw HTTP requests to the app's public webhook endpoint.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the signed material, or otherwise cryptographically or contextually verify that the header-derived `shop` matches the shop that owns the webhook payload before handing it to the handler — e.g., include these header values in `to_signable_string`, or require callers of `Registry.process` to supply/verify the expected shop out-of-band rather than trusting the header value implicitly as authenticated identity.

### Proof of Concept
1. App is installed on `attacker.myshopify.com`; attacker triggers/receives a real webhook (e.g. `orders/create`) with a valid `X-Shopify-Hmac-Sha256` computed by Shopify over the JSON body.
2. Attacker resends the identical `raw_body` and `X-Shopify-Hmac-Sha256` header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over `raw_body` only and it matches, so `Registry.process` in `lib/shopify_api/webhooks/registry.rb` proceeds.
4. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker's order data>, ...)`, causing the host application to act on attacker data under the victim shop's identity.

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
