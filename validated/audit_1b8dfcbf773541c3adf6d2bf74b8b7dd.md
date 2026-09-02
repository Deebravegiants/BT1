## Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) attribution is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC of the raw request body, then dispatches the handler using the `shop`, `topic`, `webhook_id`, and `api_version` values taken from HTTP headers that are **not** part of the signed material. Anyone who can obtain one genuinely-signed webhook delivery (e.g., an attacker who installs the app on their own store and receives real webhooks) can replay that exact body/HMAC pair while substituting a different `x-shopify-shop-domain` header, and the gem will accept it as an authentic webhook "from" the spoofed shop.

### Finding Description
`ShopifyAPI::Webhooks::Request` exposes `hmac`, `shop`, `topic`, `webhook_id`, and `api_version`, but only the raw body is included in the signable content: [1](#0-0) 

`shop` is read straight from the `shop-domain` header with no cryptographic binding to the body or to the other headers: [2](#0-1) 

`Registry.process` verifies only the HMAC of `to_signable_string` (the raw body) via `Utils::HmacValidator.validate`, then immediately trusts `request.shop`/`request.topic` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`Utils::HmacValidator.validate` and `compute_signature` confirm that only `verifiable_query.to_signable_string` (the body, for webhooks) is signed — headers are excluded from the computation: [4](#0-3) 

The gem's own documentation instructs apps to key their tenant logic directly off `data.shop` from the handler callback (e.g. `shop_domain: data.shop`), confirming that this field is treated as trusted/authoritative by design: [5](#0-4) 

**Identity binding broken:** the equality the app relies on is `shop_that_produced_this_signed_body == shop_attributed_to_the_event`. In reality the gem only proves `HMAC(secret, raw_body) == received_hmac`; it proves nothing about which shop the body belongs to. Any party capable of receiving one authentic webhook (trivially achievable by installing the app on an attacker-owned/free development store) can capture a `(raw_body, hmac)` pair and re-POST it to the app's webhook endpoint with an arbitrary `x-shopify-shop-domain` header value. `Registry.process` will accept the HMAC (unchanged body) and hand the handler a `WebhookMetadata` claiming the event belongs to the victim shop.

### Impact Explanation
This is a cross-tenant identity confusion: an attacker's own genuine webhook traffic can be attributed to a different (victim) shop inside the host application. Depending on what the webhook payload represents (e.g., `app/uninstalled`, `shop/update`, `customers/data_request`, orders, etc.) and how the host app keys persistence/side effects off `data.shop`, this can be used to poison another tenant's records, trigger uninstall/data-erasure workflows against a shop that never sent the event, or otherwise inject attacker-controlled data into another merchant's context — all without needing the app's `api_secret_key`, an access token, or any privileged credential. This matches the High-impact category of cross-tenant access via a broken identity binding.

### Likelihood Explanation
Likelihood is high for any developer/attacker who has (or creates) a store with the app installed: they receive legitimately HMAC-signed webhook deliveries for topics they subscribe to, and the gem provides no protection preventing replay of that exact body against the endpoint with a forged `shop-domain` header. No secrets need to be recovered — the attacker already legitimately possesses a valid `(body, hmac)` pair for their own store.

### Recommendation
Bind the shop (and ideally topic/webhook_id) into the value that is HMAC-verified, or otherwise cryptographically tie the header-provided `shop` to the specific signed body (e.g., validate the shop against records of registrations/subscriptions known to the app, or require the host app to cross-check `data.shop` against an independently-trusted source such as the session/shop that registered that specific `webhook_id`). At minimum, document prominently that `data.shop`/`data.topic` are unauthenticated header values and must not be trusted as tenant identifiers without additional verification.

### Proof of Concept
1. Install the target app on an attacker-controlled development store `attacker-shop.myshopify.com` and subscribe to a webhook topic (e.g. `customers/data_request`).
2. Trigger the event on `attacker-shop` so Shopify sends a real webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B`), `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Capture `B` and `H`.
4. Replay a POST to the app's webhook endpoint with the same body `B` and header `x-shopify-hmac-sha256: H`, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `HMAC(secret, B) == H`. The handler is invoked with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: B, ...)`, causing the host app to process attacker-supplied data under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-40)
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

        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
        end
```

**File:** docs/usage/webhooks.md (L20-29)
```markdown
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
