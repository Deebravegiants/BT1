## Title
Webhook Shop Attribution Not Covered by HMAC Signature Enables Cross-Tenant Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then trusts the `shopify-shop-domain` (and `topic`/`webhook-id`/`api-version`) HTTP headers — none of which are included in the signed payload — to attribute the webhook to a tenant. This breaks the intended binding "shop that produced the signed bytes == shop the handler believes sent the webhook."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read directly from HTTP headers, never validated against the signed content: [2](#0-1) 

`HmacValidator.validate` computes the signature over exactly that signable string (the body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` to build `WebhookMetadata` passed to the app's handler, with no further binding check between the header-derived `shop` and the signed body: [4](#0-3) 

Because the HMAC only proves "this body was signed by Shopify with our `client_secret`," and not "this body came from shop X," any entity that legitimately receives one authentic webhook (e.g., a malicious merchant who installs the app on their own store, shop A) can capture that `(raw_body, hmac)` pair and resend it to the app's webhook endpoint with the `shopify-shop-domain` header rewritten to shop B's domain (and `topic`/`webhook-id` similarly rewritten). `Registry.process` will still pass HMAC validation (since the body/hmac pair is untouched) and will dispatch the handler with `WebhookMetadata.shop == "shop-B.myshopify.com"`, `topic`, and `webhook_id` values chosen by the attacker rather than the ones Shopify actually signed for.

This is the identity-binding break the prompt calls out: the field acted upon by the handler (`shop`, and indirectly `topic`/`webhook_id`) is not covered by the HMAC that is supposed to authenticate the whole message.

### Impact Explanation
If the host application uses `WebhookMetadata.shop`/`topic` (as documented and demonstrated in the gem's own usage docs) to decide which tenant's data to update, delete, or resync, an attacker can forge cross-tenant webhook events — e.g., replaying an `app/uninstalled` or `customers/redact` payload from their own shop but attributed to a victim shop, or replaying arbitrary topic-typed bodies under a victim's shop domain — causing the host app to act on/for a tenant that never sent that webhook. This is a cross-tenant access primitive attributable to the gem's own verification code, matching the Critical "cross-tenant access" impact class.

### Likelihood Explanation
Requires only an actor able to install the app on any shop (a normal, low-privilege capability that any internet user can obtain by installing a public app on their own dev/trial store) to legitimately receive one authentic webhook body+HMAC pair, then replay it with edited headers to the same public webhook endpoint. No access token, `client_secret`, or elevated privilege is required — only observation of one's own legitimately delivered webhook.

### Recommendation
Bind the identifying headers into the signed/verified data, or otherwise cryptographically tie `shop`, `topic`, and `webhook_id` to the authenticated body — for example by requiring the host application/gem to cross-check the `shop-domain` header against a shop-scoped secret, or by including these header values in the HMAC computation as Shopify's other verifiable queries (`AuthQuery`) already do for `shop`, `host`, `code`, `state`, and `timestamp`: [5](#0-4) 
At minimum, document prominently that `WebhookMetadata.shop`/`topic` are unauthenticated header values and must not be trusted for tenant attribution without an additional binding check.

### Proof of Concept
1. Install the target app (or any app using this gem for webhook processing) on attacker-controlled shop `attacker-shop.myshopify.com`; trigger a webhook (e.g. `orders/create`) and capture the raw POST body and the `x-shopify-hmac-sha256` header Shopify sent.
2. Replay that exact `raw_body` and `hmac` header to the same webhook endpoint, but replace the `x-shopify-shop-domain` header value with `victim-shop.myshopify.com` (and optionally an arbitrary `topic`/`webhook-id`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes HMAC over `raw_body` — validation succeeds: [6](#0-5) 
4. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"`, even though Shopify never signed a webhook for that shop — demonstrating the cross-tenant attribution spoof.

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
